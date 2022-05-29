class get_Id:
	def __init__(self, data):
		self.comId=None
		self.Id=None
		self.data = data['linkInfoV2']['extensions']
		try:self.comId = self.data['community']['ndcId']
		except KeyError:self.comId=self.data["linkInfo"]['ndcId']
		try:self.Id=self.data["linkInfo"]["objectId"]
		except KeyError:pass
class userProfile:
	def __init__(self,data):
		self.data = data["userProfile"]
		self.userId = None
		self.level = None
		self.reputation = None
		self.nickname = None
		self.blogs = None
		try:self.userId = self.data["uid"]
		except KeyError:pass
		try:self.level = self.data["level"]
		except KeyError:pass
		try:self.reputation = self.data["reputation"]
		except KeyError:pass
		try:self.nickname=self.data["nickname"]
		except KeyError:pass
		try:self.blogs=self.data["blogsCount"]
		except KeyError:pass
class wallet:
	def __init__(self,data):
		self.data = data["wallet"]
		self.floatcoins = None
		self.coins = None
		try:self.coins = self.data["totalCoins"]
		except KeyError:pass
		try:self.floatcoins = self.dafa["totalCoinsFloat"]
		except KeyError:pass
class userProfileList:
	def __init__(self,data):
		self.data = data["userProfileList"]
		self.nickname = []
		self.userId = []
		for a in self.data:
			try:self.nickname.append(a["nickname"])
			except KeyError:pass
			try:self.userId.append(a["uid"])
			except KeyError:pass