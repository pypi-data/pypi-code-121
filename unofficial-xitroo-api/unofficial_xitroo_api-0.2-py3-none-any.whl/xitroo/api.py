import base64
import time
import requests

class xitroo():
    def __init__(self, xitroo_email, refresh_counter=5, refresh_wait=5):
        self.xemail = xitroo_email
        ts = int(format(time.time(), ".0f"))
        for i in range(refresh_counter):
            idsite = requests.get(f"https://api.xitroo.com/v1/mails?locale=de&mailAddress={self.xemail}&mailsPerPage=25&minTimestamp=0.0&maxTimestamp={str(ts + 500)}").json()
            try:
                mails = idsite["mails"][0]
                id = mails['_id']
                self.mega = requests.get("https://api.xitroo.com/v1/mail?locale=de&id=" + id).json()
                break
            except:
                print(idsite['type'])
                if i == refresh_counter:
                    break
                time.sleep(refresh_wait)


    def get_bodyHtmlStrict(self):
        return base64.b64decode(self.mega["bodyHtmlStrict"])

    def get_bodyHtml(self):
        return base64.b64decode(self.mega["bodyHtml"])

    def get_bodyText(self):
        return base64.b64decode(self.mega["bodyText"])
