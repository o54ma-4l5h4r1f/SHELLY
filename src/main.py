from lib.netcat import Netcat as nCat
 
def banner():
    print('''
▞▀▖▌ ▌▛▀▘▌  ▌ ▌ ▌
▚▄ ▙▄▌▙▄ ▌  ▌ ▝▞ 
▖ ▌▌ ▌▌  ▌  ▌  ▌ 
▝▀ ▘ ▘▀▀▘▀▀▘▀▀▘▘
by @o54ma4l5h4r1f & @Mustafa-AlShawwa
''')
 
def main():
    banner()
    nc = nCat('0.0.0.0', 1234)
    nc.listen()
    nc.interact()
 
 
if __name__ == "__main__":
    main()