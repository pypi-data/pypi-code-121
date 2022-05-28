from requests import RequestException
from orange.utils import *

def main():
    clear()
    try:
        dashboard()
    except KeyboardInterrupt:
        print("👋 Goodbye")
    except RequestException:
        print(
            "❌ I can't reach the modem"
        )

if __name__ == '__main__':
    main()