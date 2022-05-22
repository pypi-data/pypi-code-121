import os
import sys
import urllib.request
import json


class translation:

    def __init__(self, client_id, client_secret):
        self.id = client_id
        self.secret_id = client_secret

    def detect(self, text: str):
        encQuery = urllib.parse.quote(text)
        data = "query=" + encQuery
        url = "https://openapi.naver.com/v1/papago/detectLangs"
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", self.id)
        request.add_header("X-Naver-Client-Secret", self.secret_id)
        response = urllib.request.urlopen(request, data=data.encode("utf-8"))
        rescode = response.getcode()
        if (rescode == 200):
            response_body = response.read()
            result = json.loads(response_body)
            result = result['langCode']
            return result
        else:
            raise Exception("Error Code:" + rescode)

    def conver(self, target, text, results=True):

        encQuery = urllib.parse.quote(text)
        data = "query=" + encQuery
        url = "https://openapi.naver.com/v1/papago/detectLangs"
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", self.id)
        request.add_header("X-Naver-Client-Secret", self.secret_id)
        response = urllib.request.urlopen(request, data=data.encode("utf-8"))
        rescode = response.getcode()
        if (rescode == 200):
            response_body = response.read()
            result = json.loads(response_body)
            result = result['langCode']
        else:
            raise Exception("Error Code:" + rescode)

        encText = urllib.parse.quote(text)
        data = f"source={result}&target={target}&text=" + encText
        url = "https://openapi.naver.com/v1/papago/n2mt"
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", self.id)
        request.add_header("X-Naver-Client-Secret", self.secret_id)
        response = urllib.request.urlopen(request, data=data.encode("utf-8"))
        rescode = response.getcode()
        if (rescode == 200):
            response_body = response.read()
            result = json.loads(response_body)
            if results == False:
                result = result['message']

            elif results == True:
                result = result['message']['result']['translatedText']

            else:
                raise Exception("Only True or False can be entered in the 'results' field.")

            return result
        else:
            raise Exception("Error Code:" + rescode)