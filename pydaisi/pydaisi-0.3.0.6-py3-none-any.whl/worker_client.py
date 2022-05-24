import requests
import os
from dotenv import dotenv_values

class WorkerClient():
    def __init__(self, daisi_id, base_url, access_token: str = ""):
        self.daisi_id = daisi_id
        self.base_url = base_url
        self.session = requests.Session()
        access_token = (
            access_token
            or os.getenv("DAISI_ACCESS_TOKEN", "")
            or dotenv_values().get("DAISI_ACCESS_TOKEN", "")  # type: ignore
        )
        if access_token:
            self.session.headers.update({"Authorization": f"token {access_token}"})
            
    @property
    def number(self):
        res = self.session.get(f"{self.base_url}/workers/{self.daisi_id}/number")
        if res.status_code == requests.codes.ok:
            number = res.json()
        else:
            number = -1
        
        return number

    @property
    def status(self):
        res = self.session.get(f"{self.base_url}/workers/{self.daisi_id}/status")
        if res.status_code == requests.codes.ok:
            status = res.json()["message"]
        else:
            status = f"Unknown: {res.status_code}"
        
        return status

    def set(self, worker_number):
        res = self.session.post(f"{self.base_url}/workers/{self.daisi_id}", json={"worker_number": worker_number})
        if res.status_code in [requests.codes.ok, requests.codes.locked]:
            message = res.json()["message"]
        else:
            message = f"failed {res.status_code}, {res.text}"
        
        return message
