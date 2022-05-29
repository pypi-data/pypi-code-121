import sys
import silly_db

help = f"""
Silly DB v{silly_db.__version__}

more informations here:
https://github.com/byoso/silly_db/

Get some ready to use templates with 'plop'
Read the plop's help with this command line:

python3 -m silly_db.plop

"""


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print(help)
