import requests


def send_message(number, template_name, auth_token):
    hed = {'Authorization': 'Bearer ' + auth_token}
    endpoint = "https://graph.facebook.com/v13.0/112752771439980/messages"
    data = {"messaging_product": "whatsapp",
            "to": number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": "en_US"
                }
            }
            }
    response = requests.post(endpoint, json=data, headers=hed)
    print(response)
    print(response.json())
