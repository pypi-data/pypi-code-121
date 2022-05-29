import os
from xmlApiParse.parser_json import RKXMLRequest
from dotenv import load_dotenv

load_dotenv()

host = os.getenv('RKEEPER_HOST')
user_name = os.getenv('RKEEPER_USERNAME')
password = os.getenv('RKEEPER_PASSWORD')

try:
    current_request = RKXMLRequest(host=host, user_name=user_name, password=password)
except Exception as error:
    print(f"Connection error - {error}")
