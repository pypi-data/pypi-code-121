"""Management of the self-tests of the library and of each module
"""

import sys

try:
    import mfire
except Exception as excpt:
    print("Failed to import mfire")
    print()
    print("Following Exception caught :")
    print()
    print(excpt)
    sys.exit(1)

if __name__ == "__main__":
    try:
        import mfire.composite
        import mfire.configuration
        import mfire.data
        import mfire.localisation
        import mfire.mask
        import mfire.output
        import mfire.production
        import mfire.settings
        import mfire.tasks
        import mfire.text
        import mfire.utils

        print(f"{mfire.__name__} ({mfire.__version__}): selfcheck OK.")
        sys.exit(0)

    except Exception as excpt:
        print(f"{mfire.__name__} ({mfire.__version__}): selfcheck failed.")
        print()
        print("Following Exception caught :")
        print()
        print(excpt)
        sys.exit(1)
