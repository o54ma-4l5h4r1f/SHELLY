from lib.palette import colorize as C 

class Logger():
    def __init__(self):
        pass
    
    def success(self, text):
        print(C(f"[+] {text} ", 'green'))

    def info(self, text):
        print(C(f"[*] {text} ", 'white', 'bold'))

    def warn(self, text):
        print(C(f"[!] {text} ", 'magenta'))

    def error(self, text):
        print(C(f"[x] {text} ", 'red'))

    def debug(self, text):
        print(C(f"[$] {text} ", 'cyan'))