from os import getenv

from dotenv import load_dotenv

load_dotenv(verbose=True)

DART_API_KEY: str = getenv('DART_API_KEY')
'''OpenDart API Key - .env로부터 API Key를 읽어옵니다.

example key = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
'''

if not DART_API_KEY:
    raise Exception(".env에서 사용자의 API Key를 읽어오지 못했습니다.")
