import json
import urllib3
import os

http = urllib3.PoolManager()


def handler(event, context):
    function_arn = event.get("requestContext", {}).get("functionArn")
    condition = event.get("requestContext", {}).get("condition")
    error_message = event.get("responsePayload", {}).get("errorMessage")

    url = os.getenv("WEBHOOK_URL")
    payload = {
        "channel": os.getenv("CHANNEL"),
        "username": "AWS Lambda",
        "icon_emoji": ":lambda:",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Lambda Function Failure",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*Function:* {function_arn}\n"
                        f"*Condition:* {condition}\n"
                        f"*Error:* {error_message}"
                    ),
                },
            },
        ],
    }
    encoded_payload = json.dumps(payload).encode("utf-8")
    response = http.request(method="POST", url=url, body=encoded_payload)
    print(
        {
            "message": payload,
            "status_code": response.status,
            "response": response.data,
        }
    )
