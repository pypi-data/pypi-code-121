import requests
import time

MAX_RETRIES = 100
WAIT_SECONDS = 30


class RestConnect:

    def __init__(self):
        pass

    def post(self, url, json):
        for i in range(MAX_RETRIES):
            try:
                r = requests.post(url=url,json=json)

                if r is None:
                    time.sleep(WAIT_SECONDS)
                    continue

                if r.status_code != 200:
                    time.sleep(WAIT_SECONDS)
                    continue

                return r
            except requests.exceptions.ConnectionError:
                print('build http connection failed')
            time.sleep(WAIT_SECONDS)

    def post_binary(self, url, data):
        for i in range(MAX_RETRIES):
            try:
                r = requests.post(url=url,data=data)

                if r is None:
                    time.sleep(WAIT_SECONDS)
                    continue

                if r.status_code != 200:
                    time.sleep(WAIT_SECONDS)
                    continue

                return r
            except requests.exceptions.ConnectionError:
                print('build http connection failed')
            time.sleep(WAIT_SECONDS)

    def get(self, url, headers=None):
        for i in range(MAX_RETRIES):
            try:
                if headers is None:
                    r = requests.get(url=url)
                else:
                    r = requests.get(url=url,headers=headers)
                if r is None:
                    time.sleep(WAIT_SECONDS)
                    continue
                if r.status_code != 200:
                    #print(r.status_code)
                    time.sleep(WAIT_SECONDS)
                    continue
                return r
            except requests.exceptions.ConnectionError:
                print('build http connection failed')
            time.sleep(WAIT_SECONDS)