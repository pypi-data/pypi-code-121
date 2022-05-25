import sys

def main():
    if len(sys.argv) < 2:
        print('Pass search filters as parameters', '> ... | grep .exe .dll', sep='\n')
        quit(0)

    try:
        while 1:
            line = input()
            for arg in sys.argv[1:]:
                if arg in line:
                    print(line)
    except EOFError:
        pass

if __name__ == '__main__':
    main()