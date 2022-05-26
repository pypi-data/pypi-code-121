#!/usr/bin/python

class C:
    FLAG_NUM = 50  # === per_side is 50

    @staticmethod
    def red(s):
        return f"\033[31m{s}\33[0m"

    @staticmethod
    def purple(s):
        return f"\033[35m{s}\33[0m"

    @staticmethod
    def green(s):
        return f"\033[32m{s}\33[0m"

    @staticmethod
    # import platform
    # if platform.system().lower() == "linux":
    def print_(content):
        print(f"\033[41;30m{content}\33[0m")  # \33[0m can close color

    @staticmethod
    def cprint(content, n=FLAG_NUM):
        l_diff_ = n - int(len(str(content)) / 2)
        r_diff_ = n - int(len(str(content)) / 2) + 1
        C.print_(f"\033[41;30m<{l_diff_ * '='}\33[0m"
                 f"\033[40;35m{content}\33[0m"
                 f"\033[41;30m{'=' * r_diff_}>\33[0m")