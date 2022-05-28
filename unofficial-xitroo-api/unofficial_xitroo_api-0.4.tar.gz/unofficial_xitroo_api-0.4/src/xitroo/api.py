import base64
import time
import requests

class xitroo():
    def __init__(self, xitroo_email: str, refresh_counter=5, refresh_wait=5):
        self.xemail = xitroo_email
        self.refresh_c = refresh_counter
        self.refresh_w = refresh_wait

    def get_latest_inbox_raw(self):
        for i in range(self.refresh_c):
            idsite = requests.get(f"https://api.xitroo.com/v1/mails?locale=de&mailAddress={self.xemail}&mailsPerPage=25&minTimestamp=0.0&maxTimestamp={str(int(format(time.time(), '.0f')) + 500)}").json()
            try:
                mega = requests.get("https://api.xitroo.com/v1/mail?locale=de&id=" + idsite["mails"][0]['_id']).json()
                return mega
            except:
                print(idsite['type'])
                if i == self.refresh_c-1: exit()
                time.sleep(self.refresh_w)

    def get_bodyHtmlStrict(self): return base64.b64decode(self.get_latest_inbox_raw()["bodyHtmlStrict"])

    def get_bodyHtml(self): return base64.b64decode(self.get_latest_inbox_raw()["bodyHtml"])

    def get_bodyText(self): return base64.b64decode(self.get_latest_inbox_raw()["bodyText"])

    def get_subject(self): return base64.b64decode(self.get_latest_inbox_raw()["subject"]).decode("UTF-8")