from .pyssg import main


# since this is not used as a package, rather it's used as a command line tool,
#   this is never called because pyssg:main is called directly when running pyssg
if __name__ == '__main__':
    main()
