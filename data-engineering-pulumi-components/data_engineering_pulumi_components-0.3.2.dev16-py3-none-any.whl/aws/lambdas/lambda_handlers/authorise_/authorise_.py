import os
import json


def handler(event, context):

    # 1 - Log the event
    print("*********** The event is: ***************")

    authorizationToken = json.dumps(event["multiValueHeaders"]["authorisationToken"])

    characters_to_remove = '"[]"'
    for character in characters_to_remove:
        authorizationToken = authorizationToken.replace(character, "")

    # 2 - See if the person's token is valid
    if authorizationToken == os.environ["authorisationToken"]:
        auth = "Allow"
    else:
        auth = "Deny"

    # 3 - Construct and return the response
    authResponse = {
        "principalId": "abc123",
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Resource": [os.environ["api_link"]],
                    "Effect": auth,
                }
            ],
        },
    }
    return authResponse
