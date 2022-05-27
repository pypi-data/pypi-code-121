import requests
import json
from time import gmtime, strftime
import pymsteams
from soteria.handlers.db import db


class Comms():

    def __init__(self, env='test', teams_url=None, add_urls=None):

        self.env = env
        self.default_url = teams_url

        self.add_urls = add_urls

    def post_message(self, original_test_name, message, fixed=False, message_override=False):
        """ """
        test_name = original_test_name.replace('_', ' ')
        if message_override:
            message = message
        else:
            message = f"**{test_name}:** {message}"

        self.SendTeamsMessage(message, self.default_url)

    def SendTeamsMessage(self, message, webhook):

        print(f"teams message: '{message.replace('*', '')}'")
        myTeamsMessage = pymsteams.connectorcard(webhook)

        myTeamsMessage.text(message)
        try:
            myTeamsMessage.send()
        except requests.exceptions.MissingSchema:
            pass
