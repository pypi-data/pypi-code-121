__version__ = '0.1.30'

import re
import pyperclip as pc
from chilitools.utilities.backoffice import backofficeURLInput
from chilitools.api.connector import ChiliConnector
from chilitools.api.mycp import generateLoginTokenForURL, generateOAuthTokenFromCredentials, setUserType
from chilitools.utilities.defaults import STAFF_TYPE

lastURL = None

def getConnector():
  global lastURL
  if lastURL is None:
    lastURL = backofficeURLInput()
  return ChiliConnector(backofficeURL=lastURL)


def menu():
  clipboard = True
  global lastURL
  while (True):

    print("\nCHILI Publish Testing Tools")
    print("--------------------------\n")
    print("1) Generate Login Token for BackOffice URL")
    print("2) Get API Key for BackOffice URL")
    print("3) Generate Login Token for ft-nostress")
    print("4) Generate Login Token for ft-nostress-sandbox")
    print("5) Set/Change login credentials")
    print("6) Toggle copy keys to clipboard\n")
    print("7) Change BackOffice URL\n")
    if lastURL is not None: print("current backoffice URL: " + lastURL)

    option = input()

    if 'staff' in option:
      print('Succesfully enabled 2FA staff login for BackOffice')
      setUserType(userType=STAFF_TYPE)
      continue
    elif 'exit' in option:
      break

    if re.search("[0-8]", option):
      option = int(option)
      print('')


      if option == 1:
        chili = getConnector()
        token = generateLoginTokenForURL(backofficeURL=chili.backofficeURL)
        if clipboard: pc.copy(token)
        print(token)
      elif option == 2:
        chili = getConnector()
        key = chili.getAPIKey()
        pc.copy(key)
        print(key)
      elif option == 3:
        chili = ChiliConnector(backofficeURL='https://ft-nostress.chili-publish.online/ft-nostress/interface.aspx')
        token = generateLoginTokenForURL(backofficeURL=chili.backofficeURL)
        if clipboard: pc.copy(token)
        print(token)
      elif option == 4:
        chili = ChiliConnector(backofficeURL='https://ft-nostress.chili-publish-sandbox.online/ft-nostress/interface.aspx')
        token = generateLoginTokenForURL(backofficeURL=chili.backofficeURL)
        if clipboard: pc.copy(token)
        print(token)
      elif option == 5:
        print(generateOAuthTokenFromCredentials())
      elif option == 6:
        clipboard = not clipboard
      elif option == 7:
        lastURL = backofficeURLInput()

    else:
      print("That is not a valid option, please try again")

