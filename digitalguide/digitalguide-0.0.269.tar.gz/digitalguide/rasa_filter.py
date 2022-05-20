import logging
from google import auth
from telegram.ext import MessageFilter
import requests as req
from requests.exceptions import Timeout
from configparser import ConfigParser 
import os
import json
  
config = ConfigParser() 
config.read('config.ini')

logger = logging.getLogger(__name__)


class FilterRasa(MessageFilter):
    def __init__(self, intent, confidence=0.8):
        self.intent = intent
        self.confidence = confidence
        
    def filter(self, message):
        try:
            payload = json.dumps({
            "username": os.getenv('RASA_USER'),
            "password": os.getenv('RASA_PASSWORD')
            })

            token_response = req.post(config["rasa"]["url"] + "/api/auth", data=payload)
            logger.debug(token_response.json())

            RASA_TOKEN = token_response.json()["access_token"]
            response = req.post(config["rasa"]["url"] + "/api/projects/default/logs", params={"q": message.text}, headers={'Authorization': 'Bearer {}'.format(RASA_TOKEN)},  timeout = (3, 8))
            logger.debug(response.json())
        except (Timeout, KeyError) as e:
            logger.error(e)
            False
        else:
            if not response.ok:
                return False                                                         
            return response.json()["user_input"]["intent"]["name"] == self.intent and response.json()["user_input"]["intent"]["confidence"] >= self.confidence