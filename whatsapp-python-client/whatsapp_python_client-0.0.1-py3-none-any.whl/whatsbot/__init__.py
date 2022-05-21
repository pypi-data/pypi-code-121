import requests

class Whatsbot(object):
    def __init__(self, access_token=None, phone_number_id=None):
        self.access_token = access_token
        self.url = f"https://graph.facebook.com/v13.0/{phone_number_id}/messages"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.access_token),
        }
    def send_message(
        self, message, recipient_id, recipient_type="individual", preview_url=True
    ):
        data = {
    "messaging_product": "whatsapp",
    "to": recipient_id,
    "type": "template",
    "template": {
        "name": "hello_world",
        "language": {
            "code": "en_US"
        }
    }
}
        r = requests.post(f"{self.url}", headers=self.headers, json=data)
        return r.json()
