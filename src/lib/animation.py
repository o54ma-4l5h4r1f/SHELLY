import threading
import sys
import time

class Loading(threading.Thread):
	def __init__(self, text):
		super().__init__()
		self.animation_chars = ['[⣾]', '[⣷]', '[⣯]', '[⣟]', '[⡿]', '[⢿]', '[⣻]', '[⣽]'] # "|/-\\"
		self.running = False
		self.text = text
		self.start()
	
	def run(self):
		self.running = True
		try:
			while self.running:
				print('\r', flush=True, end='')
				for char in self.animation_chars:
					# i = (i + 1) % len(symbols)
					print(f'\r{char} {self.text}', flush=True, end=' ')
					time.sleep(0.1)
		except:
			self.stop()
		
	def stop(self):
		self.running = False
		self.join()