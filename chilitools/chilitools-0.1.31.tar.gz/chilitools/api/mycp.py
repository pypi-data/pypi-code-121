import requests
from os import getenv
from chilitools.settings.config import LOGIN_FILE
from chilitools.utilities.defaults import STAFF_TYPE, USER_TYPE
from chilitools.utilities.file import checkForFile, readFile, writeFile


def getCredentials() -> dict:
  if getenv('CHILI_PUBLISH_USERNAME') is not None and getenv('CHILI_PUBLISH_PASSWORD') is not None:
    login = {'type':STAFF_TYPE, 'credentials': { 'Username': getenv('CHILI_PUBLISH_USERNAME'), 'Password': getenv('CHILI_PUBLISH_PASSWORD') }}
  elif checkForFile(fileName=LOGIN_FILE):
    login = readFile(fileName=LOGIN_FILE, isJSON=True)
  else:
    login = inputCredentials()
  return login

def inputCredentials() -> dict:
  print("Please enter your CHILI username")
  username = input().strip()
  print("Please enter your CHILI password")
  password = input().strip()
  login = {'type':USER_TYPE, 'credentials': { 'Username': username, 'Password': password }}
  writeFile(fileName=LOGIN_FILE, data=login, isJSON=True)
  return login

def setUserType(userType: str) -> bool:
  if checkForFile(fileName=LOGIN_FILE):
    login = readFile(fileName=LOGIN_FILE, isJSON=True)
    login['type'] = userType
  writeFile(fileName=LOGIN_FILE, data=login, isJSON=True)

def generateOAuthTokenFromCredentials(login: dict = None) -> str:
  if login is None: login = getCredentials()
  if login['type'] == STAFF_TYPE:

    requestURL = "https://my.chili-publish.com/api/v1/auth/login"

    requestHeaders = {
        "Content-Type":"application/json",
        "accept": "*/*"
    }
    response = requests.post(url=requestURL, headers=requestHeaders, json=login['credentials'])

    if response.status_code != 200:
      return f"There was an error generating an OAuth Bearer Token. Status Code: {response.status_code}. Text: {response.text}"
    else:
      return response.json()['token']
  return "This method uses Azure AD OAuth login and is reserved for CHILI Staff"

def generateLoginTokenForURL(backofficeURL: str) -> str:
  login = getCredentials()
  if login['type'] == STAFF_TYPE:
    requestURL = "https://my.chili-publish.com/api/v1/backoffice/generate"

    requestHeaders = {
      "content-type":"application/json",
      "accept": "*/*",
      "authorization": "Bearer " + generateOAuthTokenFromCredentials(login=login)
    }

    requestJSON = {
      "Url":backofficeURL
    }

    response = requests.post(url=requestURL, headers=requestHeaders, json=requestJSON)

    if response.status_code != 200:
      return f"There was an error generating an login token. Status Code: {response.status_code}. Text: {response.text}"
    else:
      return response.json()['token']
  return "This method uses Azure AD OAuth login and is reserved for CHILI Staff"

