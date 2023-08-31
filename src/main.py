import sys
import socket
import getopt
import threading
import subprocess
from lib.netcat import Netcat as nCat

def usage():
	print('''
		SHELLY.py -l -p <port>
		-l, --listen                (listen on specified host/port)
		-c, --command               (initialize a shell)
		...
		...
	''')

def banner():
	print('''
▞▀▖▌ ▌▛▀▘▌  ▌ ▌ ▌
▚▄ ▙▄▌▙▄ ▌  ▌ ▝▞ 
▖ ▌▌ ▌▌  ▌  ▌  ▌ 
▝▀ ▘ ▘▀▀▘▀▀▘▀▀▘▘
by @o54ma4l5h4r1f''')

def main():
	banner()
	nc = nCat()
	nc.listen('0.0.0.0', 1234)
	nc.interact()

if __name__ == "__main__":
	main()