import base64
import time
import requests

class xitroo():
    def __init__(self, xitroo_email: str, refresh_counter=5, refresh_wait=5):
        self.xemail = xitroo_email
        for i in range(refresh_counter):
            idsite = requests.get(f"https://api.xitroo.com/v1/mails?locale=de&mailAddress={self.xemail}&mailsPerPage=25&minTimestamp=0.0&maxTimestamp={str(int(format(time.time(), '.0f')) + 500)}").json()
            try:
                self.mega = requests.get("https://api.xitroo.com/v1/mail?locale=de&id=" + idsite["mails"][0]['_id']).json()
                break
            except:
                print(idsite['type'])
                if i == refresh_counter: break
                time.sleep(refresh_wait)

    def get_bodyHtmlStrict(self): return base64.b64decode(self.mega["bodyHtmlStrict"])

    def get_bodyHtml(self): return base64.b64decode(self.mega["bodyHtml"])

    def get_bodyText(self): return base64.b64decode(self.mega["bodyText"])

    def get_subject(self): return base64.b64decode(self.mega["subject"])