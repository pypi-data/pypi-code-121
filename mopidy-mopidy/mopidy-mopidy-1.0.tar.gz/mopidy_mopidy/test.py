from utils import Utils

import requests

import socket
print(socket.gethostname())

print(socket.gethostbyname(socket.gethostname()))

#exit(0)

url = "http://192.168.2.109:6680/mopidy/rpc"
payload = {
  "method": "core.playback.get_time_position",
  "jsonrpc": "2.0",
  "params":{},
          "id": 0
}
response = requests.post(url, json=payload).json()
print(response)
#print(response['result']['track']['uri'])
#for track in response['result']:
#  track['track']['uri'] = 'mopidymopidy:track:'+track['track']['uri']
#  print(track)
#for res in response['result']:
#  print(res)
