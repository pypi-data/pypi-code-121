import hashlib
from hmac import compare_digest

class SecurityUtils():

	def hash(self, strInput):
		h = hashlib.sha512(strInput.encode())
		return h.hexdigest()
		
	def getUserHashPassword(self, userId, password):
		strInput = userId + password	
		return self.hash(strInput)

	def verify(self, userId, password, hexdigest):
		hashHexdigest = self.getUserHashPassword(userId, password)
		return compare_digest(hashHexdigest, hexdigest)
		