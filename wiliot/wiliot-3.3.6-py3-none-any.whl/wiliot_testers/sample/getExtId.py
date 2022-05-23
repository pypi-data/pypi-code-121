'''
Created on Dec 27, 2021

@author: davidd
'''
from os import environ
from urllib.parse import quote
import http
from json import loads
from SampleTest import PAYLOAD_START, NIBS_IN_BYTE, CRC_START
import time
from tkinter import simpledialog
import tkinter

if __name__ == '__main__':
    username = environ.get('FUSION_AUTH_USER')
    username = quote(username)
    password = environ.get('FUSION_AUTH_PASSWORD')
    password = quote(password)
    conn = http.client.HTTPSConnection("api.wiliot.com")
    headers = {'accept': "application/json"}
    conn.request("POST", "/v1/auth/token?password=" + password + "&username=" + username, headers=headers)
    res = conn.getresponse()
    data = res.read()
    tokens = loads(data.decode("utf-8"))
    # print(tokens)
    token = tokens['access_token']
    print('Token received successfully.')

    gtin = None
    curId = None
    reelId = None

    conn = http.client.HTTPSConnection("api.wiliot.com")
    root = tkinter.Tk()
    root.eval('tk::PlaceWindow . center')
    root.lift()
    root.attributes("-topmost", True)
    root.attributes("-topmost", False)
    root.withdraw()

    while True:
        packetRaw = simpledialog.askstring(title="Ext ID", prompt="Enter packet raw:")
        if packetRaw is None or packetRaw.strip() == '':
            continue
        packetTime = 0.1

        packetPayload = packetRaw[PAYLOAD_START * NIBS_IN_BYTE:]
        packetPayload = packetPayload[: CRC_START * NIBS_IN_BYTE]
        # print(packetRaw)
        # print(packetPayload)

        payload = '{\"gatewayType\":\"Manufacturing\",\"gatewayId\":\"manufacturing-gateway-id\",\"timestamp\":' + str(time.time()) + ',\"packets\":[{\"timestamp\":' + str(packetTime * (10 ** 6)) + ',\"payload\":\"' + packetPayload + '\"}]}'

        headers = {
            'accept': "application/json",
            'authorization': "Bearer " + token + "",
            'content-type': "application/json"
        }

        owner = 'wiliotmnf'
        conn.request("POST", f"/v1/owner/{owner}/resolve", payload, headers)

        res = conn.getresponse()
        data = res.read()

        data = loads(data.decode("utf-8"))
        # print(data)

        if 'externalId' in data['data'][0].keys() and data['data'][0]['externalId'] != 'unknown':
            try:
                fullData = data['data'][0]['externalId']
                gtin = ')'.join(fullData.split(')')[:2]) + ')'
                tagData = fullData.split(')')[2]
                curId = tagData.split('T')[1].strip("' ")
                reelId = tagData.split('T')[0].strip("' ")
            except:
                pass
        print(curId, reelId, gtin)
