import sys


if __name__ == "__main__":
    if "--api" in sys.argv:
        from .API.service import run
        run()
    elif "--disaggregator":
        from .Disaggregator.service import run
        run()
