from yamlist import yamlib
from yamlist import calculator

def main():
    src = yamlib.load_yaml()
    config = {}
    dst = calculator.calc(src, config)
    yamlib.save_yaml(dst)

if __name__ == "__main__":
    main()

