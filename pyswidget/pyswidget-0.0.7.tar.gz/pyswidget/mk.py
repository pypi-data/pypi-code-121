import requests
import asyncio

url = "https://192.168.1.134/api/v1/state"

payload={}
headers = {
  'x-secret-key': 'letmein23'
}

response = requests.request("GET", url, headers=headers, data=payload, verify=False)

from pprint import pprint
print("STATE")
print(response.text)
pprint(response.json())

url = "https://192.168.1.134/api/v1/summary"
response = requests.request("GET", url, headers=headers, data=payload, verify=False)
print("SUMMARY")
pprint(response.json())


from device import SwidgetDevice
from swidgetdimmer import SwidgetDimmer
from swidgetoutlet import SwidgetOutlet
async def main():

  a = SwidgetDimmer('192.168.1.134', 'letmein23', False)
  print(a)
  await a.update()
  await a.turn_on()
  print(await(a.total_consumption()))
  print(await(a.get_child_comsumption(0)))
  await a.set_brightness(50)
  await a.turn_off()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
