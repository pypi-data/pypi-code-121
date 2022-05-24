
def _f() -> None:
    import sys
    if sys.version_info < (3, 6):
        print("Requires Python 3.6+")
        sys.exit(1)
_f()
del _f
