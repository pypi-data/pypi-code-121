# from check import check
from smsitai import send

import datetime
import json

import dotenv
import requests
import re
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.
#
#

USE_SPECIFIED = 0
USE_ALL_DEVICES = 1
USE_ALL_SIMS = 2


class SMSit:
    def __init__(self, api_key):
        self.server = 'https://www.smsit.ai/smsgateway'
        self.api_key = api_key

    def send_message(self, number, message, schedule=None, devices=0, isMMS=False, attachments=None, prioritize=False):
        url = f'{self.server}/services/send.php'
        message_type = 'mms' if isMMS else 'sms'
        message_priority = 1 if prioritize else 0
        number = self.get_phone_number(number)
        print(f'number: {number}\nmessage: {message}')
        post_data = dict(number=number,
                         message=message,
                         schedule=schedule,
                         key=self.api_key,
                         devices=devices,
                         type=message_type,
                         attachments=attachments,
                         prioritize=message_priority)
        r = requests.post(url, data=post_data)
        response = json.loads(r.text)
        print(f'response: {response}')
        messages: dict = response['messages']
        # print(response)
        return messages

    def send_messages(self, messages, option=USE_SPECIFIED, devices=[], schedule=None, use_random_device=False):
        url = f'{self.server}/services/send.php'
        for m in messages:
            m['number'] = self.get_phone_number(m['number'])
        # messages = []
        # for num, mes in message_pairs:
        #     messages.append(dict(number=get_phone_number(num), message=mes))
        post_data = dict(messages=json.dumps(messages),
                         schedule=schedule,
                         key=self.api_key,
                         devices=devices,
                         option=option,
                         use_random_device=use_random_device)
        r = requests.post(url, data=post_data)
        response = r.json()
        print(f'response: {response}')
        return response['data']['messages']

    def get_phone_number(self, phone_number):
        phone_number = re.sub(rf'(?ims)[\s\-()]', '', phone_number)
        num_digits = len(phone_number)
        return phone_number