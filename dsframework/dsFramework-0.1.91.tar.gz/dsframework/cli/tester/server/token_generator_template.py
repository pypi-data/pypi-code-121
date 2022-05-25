from typing import Any
import requests
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
import base64
import json
from datetime import datetime, timedelta

##
# @file
# @brief token_generator -  Generate token from a given account, host and target_audience (which is stored in advance)

class tokenGenerator():
	# account example - original_project_name@dozi-stg-ds-apps-1.iam.gserviceaccount.com
	# audience example - 1042519062770-rghbs1ied8kno7l00mlnko5r7sgjea2o.apps.googleusercontent.com
	conf = {
		"STG_Conf": {
			"account": '', # need to get from dev ops
			"host": 'dozi-stg-ds-apps-1',
			"target_audience": '1042519062770-rghbs1ied8kno7l00mlnko5r7sgjea2o.apps.googleusercontent.com', # need to get from dev ops
			"iap": True,
		},
		"PRD_Conf": {
			"account": '',  # need to get from dev ops
			"host": 'dozi-prd-ds-apps-1',
			"target_audience": '484284403458-lpmc6edp4b6rd2383dgpkiq5a9ngkpbc.apps.googleusercontent.com',  # need to get from dev ops
			"iap": True,
		}
	}
	tokens = {
		"STG_Conf": '',
		"PRD_Conf": '',
	}

	def generateToken(self, type):
		"""! Generate token by the help of the type, and store it in the self.tokens[type]
		@verbatim
		Args:
			type: STG_Conf or PRD_Conf
		Returns:
			tokens[type] : tokens associated with the relevant credentials
		@endverbatim
		"""

		if self.isExpired(type):
			self.resetToken(type)
		if not type or not self.conf[type]:
			return ''
		conf: Any = self.conf[type]
		if not conf['account']:
			print('please specify account')
			return ''
		if not conf['target_audience']:
			print('please specify target audience')
			return ''
		if not self.tokens[type]:
			credentials = self.authorize()
			token = self.getToken(credentials, conf)
			if self.conf[type]['iap']:
				token = self.buildIdToken(credentials, token, conf)
			self.tokens[type] = token

		return self.tokens[type]

	def authorize(self):
		"""! Authorize return if we got credentials on google.
		@verbatim
		Returns:
			credentials : return google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
		@endverbatim
		"""
		return GoogleCredentials.get_application_default()

	def getToken(self, credentials, conf):
		"""! getToken Method, using credentials and request for token.

		Args:
			credentials : ServiceAccount credentials
			conf (not in use): dictionary including relevant fields like: account,project,target_audience,iap.
		Returns:
			token : jwtToken
		"""
		client_id = credentials.client_id
		client_secret = credentials.client_secret
		aud = credentials.token_uri
		iat = int(datetime.now().timestamp())
		one_hours_from_now = datetime.now() + timedelta(hours=1)
		exp = int(one_hours_from_now.timestamp())
		service = discovery.build('iam', 'v1', credentials=credentials)

		name = f'projects/{conf["host"]}/serviceAccounts/{conf["account"]}'
		data ={
			'url': f'https://iam.googleapis.com/v1/projects/-/serviceAccounts/{conf["account"]}:signJwt',
			'data': {
				'payload': json.dumps({"aud": aud,"target_audience": conf["target_audience"],"sub": conf["account"],"iss": conf["account"],"iat": iat, "exp": exp})
			}
		}
		request = service.projects().serviceAccounts().signJwt(name=name, body={'payload': data["data"]["payload"]})
		response = request.execute()
		return response['signedJwt']

	def buildIdToken(self, client, jwtToken, conf):
		"""! BuildIdToken method, send the user to their OpenID Provider with an authentication request and get the id_token.
		In General:
		The id_token value contains the information about the user's authentication.
		The ID token resembles the concept of an identity card, in a standard JWT format, signed by the OpenID Provider (OIDP).

		@verbatim
		Args:
			client : Not in use
			jwtToken : Authentication
			conf : dictionary including relevant fields like: account,project,target_audience,iap.
		Returns:
			token : id_token
		@endverbatim
		"""
		try:
			data = {
				"method": 'post',
				"url": 'https://www.googleapis.com/oauth2/v4/token',
				"data": {
					'grant_type': "urn:ietf:params:oauth:grant-type:jwt-bearer",
					'assertion': jwtToken
				}
			}
			# print('data', data)
			result = requests.post(data['url'], data['data'])
			if result and result.content:
				parsed = json.loads(result.content)
				print("[refreshTokens] token for host " + conf['host'] + " refreshed successfully")
				return parsed['id_token']
			else:
				print('no data.id_token returned from googleapis:signJwt')
		except Exception as ex:
			print("[refreshTokens] token for host " + conf['host'] + " failed to refresh")
			print(ex)

	def isExpired(self, type):
		"""! Is Expired method , tell us whether the token has expired or not.
		@verbatim
		Args:
			type : STG_Conf or PRD_Conf
		Returns:
			isExpired : bool
		@endverbatim
		"""
		isExpired = True
		if self.tokens[type]:
			decoded = self.parse_id_token(self.tokens[type])
			if decoded and int(decoded['exp']) > int(datetime.now().timestamp()):
				isExpired = False
		return isExpired

	def isExpiredToken(self, token):
		isExpired = True
		decoded = self.parse_id_token(token)
		if decoded and int(decoded['exp']) > int(datetime.now().timestamp()):
			isExpired = False
		return isExpired

	def resetToken(self, type):
		"""! Reset the token
		@verbatim
		Args:
			type : STG_Conf or PRD_Conf
		@endverbatim
		"""
		self.tokens[type] = ''

	@staticmethod
	def parse_id_token(token: str) -> dict:
		"""! Parse Google OAuth2.0 id_token payload
		An ID token has the following structure: Base64(JOSE header).Base64(Payload).Base64(Signature)
		"""
		parts = token.split(".")
		if len(parts) != 3:
			raise Exception("Incorrect id token format")
		payload = parts[1]
		padded = payload + "=" * (4 - len(payload) % 4)
		decoded = base64.b64decode(padded)
		return json.loads(decoded)


if __name__ == '__main__':
	t = tokenGenerator()
	t = t.generateToken('STG_Conf')
	print(t)

