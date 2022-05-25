import json

import requests


class NotificationUtil:
    def post_message_to_slack(self, text, blocks=None):
        API_ENDPOINT = "https://hooks.slack.com/services/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"
        slack_data = {'text': text}
        response = requests.post(
            API_ENDPOINT, data=json.dumps(slack_data),
            headers={'Content-Type': 'application/json'}
        )
