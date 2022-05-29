import os
import requests
import base64
import json
import time
import hmac
import json_minify
import functools
import hashlib
import hashlib
import threading
import datetime
import binascii
import uuid
from aminolib import objects
print("Discord\thttps://discord.gg/BnAFAPsc\naminolib.py 1.1.1")
class Client:
	def __init__(self, device: str=None):
		if device is not None:self.device = device
		else:self.device = self.deviceId()
		self.api = "https://service.narvii.com/api/v1"
		self.uuid = str(uuid.uuid4())
		self.headers = {"NDCDEVICEID":self.device,"SMDEVICEID":self.uuid,"Accept-Language":"en-EN","Content-Type": "application/json; charset=utf-8","User-Agent":"Dalvik/2.1.0 (Linux; U; Android 7.1.2; vmos Build/NZH54D; com.narvii.amino.master/3.5.34180)","Host":"service.narvii.com","Accept-Encoding":"gzip","Connection":"Keep-Alive"}
		self.sid, self.userId = None, None
	
	def deviceId(self):
		urandom = os.urandom(20)
		return ("42" + urandom.hex() + hmac.new(bytes.fromhex("02B258C63559D8804321C5D5065AF320358D366F"), b"\x42" + urandom, hashlib.sha1).hexdigest()).upper()
		
	def sig(self, data):
		return base64.b64encode(bytes.fromhex("42") + hmac.new(bytes.fromhex("F8E7A61AC3F725941E3AC7CAE2D688BE97F30B93"), data.encode("utf-8"),hashlib.sha1).digest()).decode("utf-8")
		
	def decode_sid(self, sid: str):
		return json.loads(base64.b64decode(functools.reduce(lambda a, e: a.replace(*e), ("-+", "_/"), sid + "=" * (-len(sid) % 4)).encode())[1:-20].decode())
		
	def timezone(self):
		hour = datetime.datetime.utcnow().hour
		if hour==1:timezone=-120
		if hour==2:timezone=-180
		if hour==3:timezone=-240
		if hour==4:timezone=-300
		if hour==5:timezone=-360
		if hour==6:timezone=-420
		if hour==7:timezone=-480
		if hour==8:timezone=-540
		if hour==9:timezone=-600
		if hour==10:timezone=-660
		if hour==11:timezone=-720
		if hour==12:timezone=-780
		if hour==13:timezone=+600
		if hour==14:timezone=+540
		if hour==15:timezone=+480
		if hour==16:timezone=+420
		if hour==17:timezone=+360
		if hour==18:timezone=+300
		if hour==19:timezone=+240
		if hour==20:timezone=+180
		if hour==21:timezone=+120
		if hour==22:timezone=+60
		if hour==23:timezone=+0
		return timezone
	
	def sid_to_userId(self, sid: str):
		return self.decode_sid(sid)["2"]
	
	def sid_to_ip(self, sid: str):
		return self.decode_sid(sid)["4"]
		
	def login_sid(self, sid: str):
		self.sid, self.userId = sid, self.decode_sid(sid)["2"]
		
	def login(self ,email: str, password: str):
		data = json.dumps({"email": email, "secret": f"0 {password}", "deviceID": self.device, "clientType": 100, "action": "normal", "timestamp": (int(time.time() * 1000))})
		self.headers["NDC-MSG-SIG"] = self.sig(data = data)
		req = requests.post(f"{self.api}/g/s/auth/login", data = data, headers = self.headers)
		if req.status_code!= 200:print(req.json()["api:message"])
		try:self.sid, self.userId = req.json()["sid"], req.json()["account"]["uid"]
		except:pass
	
	def get_from_url(self,link:str):
		req = requests.get(f"{self.api}/g/s/link-resolution?q={link}",headers = self.headers).json()
		return objects.get_Id(req)
	
	def join_community(self, comId: int):
		data = json.dumps({"timestamp" : int(time.time()*1000)})
		self.headers["NDC-MSG-SIG"]=self.sig(data=data)
		req = requests.post(f"{self.api}/x{comId}/s/community/join?sid={self.sid}", data = data, headers = self.headers)
		if req.status_code!=200:print(req.json()["api:message"])
		
	def check_In(self, comId: int):
		data = json.dumps({"timezone": self.timezone(),"timestamp": int(time.time() *1000)})
		self.headers["NDC-MSG-SIG"] = self.sig(data = data)
		req = requests.post(f"{self.api}/x{comId}/s/check-in?sid={self.sid}",data=data, headers=self.headers)
		if req.status_code!=200:print(req.json()["api:message"])
		
	def check_lottery(self, comId: int):
		data = json.dumps({"timezone": self.timezone(), "timestamp": int(time.time() * 1000)})
		self.headers["NDC-MSG-SIG"] = self.sig(data = data)
		req = requests.post(f"{self.api}/x{comId}/s/check-in/lottery?sid={self.sid}", data = data, headers = self.headers)
		if req.status_code!=200:print(req.json()["api:message"])
		
	def get_user_info(self, comId: int=None, userId: str=None):
		if comId is None:
			req = requests.get(f"{self.api}/g/s/user-profile/{userId}",headers=self.headers)
		if comId is not None:
			req = requests.get(f"{self.api}/x{comId}/s/user-profile/{userId}",headers=self.headers)
		if req.status_code!=200:print(req.json()["api:message"])
		return req.json()
		
	def get_wallet(self):
		req= requests.get(f"{self.api}/g/s/wallet?sid={self.sid}", headers=self.headers).json()
		return objects.wallet(req)
		
	def send_active(self, comId: int, timeslist: list = None):
		timezone = self.timezone()
		data = json_minify.json_minify(json.dumps({"userActiveTimeChunkList": [{"start": timezone, "end": timezone+300}for i in range(20)], "timestamp": int(time.time() * 1000), "optInAdsFlags": 2147483647, "timezone": timezone}))
		if timeslist: data["userActiveTimeChunkList"] = timers
		self.headers["NDC-MSG-SIG"] = self.sig(data = data)
		req = requests.post(f"{self.api}/x{comId}/s/community/stats/user-active-time?sid={self.sid}", data = data, headers = self.headers)
		if req.status_code!=200:print(req.json()["api:message"])
		
	def join_chat(self, comId : int = None, chatId: str = None):
		if comId is not None:req = requests.post(f"{self.api}/x{comId}/s/chat/thread/{chatId}/member/{self.userId}?sid={self.sid}",headers=self.headers)
		if comId is None:req = requests.post(f"{self.api}/g/s/chat/thread/{chatId}/member/{self.userId}?sid={self.sid}", headers=self.headers)
		if req.status_code!=200:print(req.json()["api:message"])
		
	def transactionId(self):
		transactionId = str(uuid.UUID(binascii.hexlify(os.urandom(16)).decode("ascii")))
		return transactionId
		
	def transfer_coins(self, comId: int=None,coin: int=None, blogId: int= None):
		data = json.dumps({"coins": coin,"tippingContext": {"transactionId": self.transactionId()},"timestamp": int(time.time() * 1000)})
		self.headers["NDC-MSG-SIG"] = self.sig(data = data)
		req = requests.post(f"{self.api}/x{comId}/s/blog/{blogId}/tipping?sid={self.sid}", headers=self.headers, data=data)
		if req.status_code!=200:print(req.json()["api:message"])
		
	def follow(self, comId : int=None, userId: str=None):
		if comId is None:
			req = requests.post(f"{self.api}/g/s/user-profile/{userId}/member?sid={self.sid}", headers=self.headers)
		if comId is not None:
			req = requests.post(f"{self.api}/x{comId}/s/user-profile/{userId}/member?sid={self.sid}",headers = self.headers)
		if req.status_code!=200:print(req.json()["api:message"])
		
	def unfollow(self, comId: int = None, userId: str = None):
		if comId is None:
			req = requests.post(f"{self.api}/g/s/user-profile/{userId}/member/{self.userId}?sid={self.sid}",headers=self.headers)
		if comId is not None:
			req = requests.post(f"{self.api}/x{comId}/s/user-profile/{userId}/member/{self.userId}?sid={self.sid}",headers=self.headers)
		if req.status_code!=200:print(req.json()["api:message"])
		
	def get_all_users(self, comId: int,start:int=0,size:int=25):
		req = requests.get(f"{self.api}/x{comId}/s/user-profile?type=recent&start={start}&size={size}",headers = self.headers)
		if req.status_code!=200:print(req.json()["api:message"])
		return objects.userProfileList(req.json())
		
	def get_online_users(self,comId:int = None,start:int=0, size:int=25):
		req = requests.get(f"{self.api}/x{comId}/s/live-layer?topic=ndtopic:x{comId}:online-members&start={start}&size={size}",headers=self.headers)
		if req.status_code!=200:print(req.json()["api:message"])
		return objects.userProfileList(req.json())
		
	def subscribe(self, comId: int=None, userId: str=None, Renew: str= False):
		transactionId = str(uuid.UUID(binascii.hexlify(os.urandom(16)).decode("ascii")))
		data = json.dumps({"paymentContext": {"transactionId":transactionId,"isAutoRenew": Renew},"timestamp": int(time.time()*1000)})
		self.headers["NDC-MSG-SIG"]=self.sig(data)
		req = requests.post(f"{self.api}/x{comId}/s/influencer/{userId}/subscribe?sid={self.sid}",headers=self.headers,data=data)
		if req.status_code!=200:print(req.json()["api:message"])
		return req.json()
	
	def online(self, comId: int=None, status:int=None):
		data = json.dumps({"onlineStatus": status,"duration": 86400,"timestamp":int(time.time()*1000)})
		self.headers["NDC-MSG-SIG"]=self.sig(data)
		req = requests.post(f"{self.api}/x{comId}/s/user-profile/{self.userId}/online-status?sid={self.sid}",data=data,headers=self.headers)
		if req.status_code!=200:print(req.json()["api:message"])
		return req.json()