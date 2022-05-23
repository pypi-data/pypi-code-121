import datetime
import json

import dotenv
import requests
import re
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.
#
#


# dotenv_vals = dotenv.dotenv_values('.env')
# print(dotenv_vals)
# smsIt = SMSit(dotenv_vals['API_KEY'])
# messages = []
# for i in range(0, 1):
#     n = '(210) 310-9760'
#     m = f'test #{i}\nsent:{datetime.datetime.now()}'
#     messages.append(dict(number=n, message=m))
#     # print(f'SENDING MESSAGE:\ti={i}\tnumber: {n}\tmessage: {m}')
#     # send_message(n, m)
#     # get_phone_number(n)
# smsIt.send_messages(messages)
# print(f'messages: {messages}')
