### Testprogram for aiohttp ###

import aiohttp
import asyncio
import json

async def fetch(client, url):
    async with client.get(url) as resp:
        # assert resp.status == 200
        print(resp.status)
        return await resp.text()

async def getSystem(client):
    url = "http://192.168.2.21/action/welcomeGet"
    async with client.get(url) as resp:
        assert resp.status == 200
        return await resp.text()


async def main():
    username = "admin"
    password = "Am3sadssads2o16"
    url = "http://192.168.2.21/action/login"
    auth = None
    if username != None and password != None:
        auth = aiohttp.BasicAuth(login=username, password=password, encoding='utf-8')

    async with aiohttp.ClientSession(auth=auth) as client:
        # Login
        html = await fetch(client, url)
        print("action/login")
        print(html)

        # Get System Info
        system = await getSystem(client)
        print("/action/welcomeGet")
        print(system)

        # Clean JSON
        json_data = json.loads(system)["updates"]
        # system_json = system.json()
        # json_data = system_json["updates"]
        print("  Hardware-Version: %s ", json_data["rf_ver"])
        print("  Firmware-Version: %s ", json_data["em_ver"])


loop = asyncio.get_event_loop()
loop.run_until_complete(main())


