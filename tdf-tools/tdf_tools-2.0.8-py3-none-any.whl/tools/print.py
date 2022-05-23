import sys


class Print:
    def line():
        print(
            "------------------------------------------------------------------------"
        )
        sys.stdout.flush()

    def str(content: str):
        print(content)
        sys.stdout.flush()

    def debug(content: str):
        print("============= debug info start=============")
        print(content)
        print("============= debug info end=============")
        sys.stdout.flush()

    def stage(content: str):
        print("\033[0;32mStage：{0} \033[0m".format(content))
        sys.stdout.flush()

    def title(content: str):
        print("\033[0;32m<-----{0}----> \033[0m".format(content))
        sys.stdout.flush()

    def warning(content: str):
        print("\033[0;33m<-----{0}----> \033[0m".format(content))
        sys.stdout.flush()

    def error(content: str, shouldExit=True):
        print("\033[0;31m {0} \033[0m".format(content))
        sys.stdout.flush()
        if shouldExit:
            exit(-1)
