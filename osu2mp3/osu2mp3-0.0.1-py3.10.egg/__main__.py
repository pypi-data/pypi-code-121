import sys
from .args import parser
from .app.app import App

def main():
    arg_parser = parser()

    if not len(sys.argv) > 1:
        arg_parser.print_help()
        sys.exit(1)

    args = arg_parser.parse_args()

    app = App(input_dir_path=args.input, output_dir_path=args.output)
    app.run(args.silent)

if __name__ == "__main__":
    main()
