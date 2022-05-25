import shutil
import os
import sys

def main():
    if shutil.which(sys.argv[-1]):
        print(shutil.which(sys.argv[-1]))
        return
    
    with open(os.path.expanduser('~\\.macros.doskey')) as file:
        list_file = file.read().splitlines()
        for i in list_file:
            ind = i.index('=')
            if sys.argv[-1] == i[:ind]:
                print(f'"{sys.argv[-1]}" aliased in "~\\.macros.doskey"')
                return
    
    print('Command not found')

if __name__ == '__main__':
    main()