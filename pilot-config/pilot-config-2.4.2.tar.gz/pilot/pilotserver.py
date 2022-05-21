import lazy_import

import os
import jwt
import time
import datetime
sys = lazy_import.lazy_module("sys")
time = lazy_import.lazy_module("time")
requests = lazy_import.lazy_module("requests")
bugsnag = lazy_import.lazy_module("bugsnag")
os = lazy_import.lazy_module("os")
yaml = lazy_import.lazy_module("yaml")
getpass = lazy_import.lazy_module("getpass")
json = lazy_import.lazy_module("json")
qrcode_terminal = lazy_import.lazy_module("qrcode_terminal")
from uuid import uuid4
Enum = lazy_import.lazy_callable("enum.Enum")
#from enum import Enum

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

from colorama import Fore
from colorama import Style
from colorama import init

from .sbc import Sbc

class RegisterNodeStatus(Enum):
  FAILED = -1
  OK = 0
  CODE_NOT_FOUND = 1
  COULD_NOT_CREATE = 2
  COULD_NOT_UPDATE = 3
  MAC_ALREADY_USED = 4

class PilotServer():
  pilot_server = 'https://gql.pilotnexus.io/v1/graphql'
  oauth_token_url = "https://amescon.eu.auth0.com/oauth/token"
  oauth_device_code_url = "https://amescon.eu.auth0.com/oauth/device/code"

  pilot_dir = '/etc/pilot/'
  nodeconfname = 'pilotnode.yml'
  authfilename = 'auth.json'

  pilot_home_dir = os.path.expanduser('~/.pilot')
  authfile = os.path.join(pilot_home_dir, authfilename)

  client_id = 'hG0Kh6oMY6A2dMUjyjAbTQPTcd8syl58'
  audience = [ "https://api.pilotnexus.io", "https://amescon.eu.auth0.com/userinfo" ]

  keys = None
  tokenset = None
  decoded = None

  terminal = True
  sbc = None

  def __init__(self, sbc: Sbc):
    self.sbc = sbc
    if not os.path.exists(self.pilot_home_dir):
      os.makedirs(self.pilot_home_dir)
    
    try:
      keys = requests.get("https://amescon.eu.auth0.com/.well-known/jwks.json").json()['keys']
      self.keys = [ key for key in keys if key['alg'] == 'RS256' ][0]
    except:
      pass

    

  def loadnodeconf(self):
    nodeconffile = self.pilot_dir + self.nodeconfname
    nodeconf = None
    try:
      nodeconf = yaml.load(self.sbc.getFileContent(nodeconffile), Loader=yaml.FullLoader)
    except:
      nodeconf = None
    return nodeconf
  
  def savenodeconf(self, nodeconf):
    nodeconffile = self.pilot_dir + self.nodeconfname
    nodeconfcontent = yaml.dump(nodeconf, default_flow_style=False)
    return self.sbc.setFileContent(nodeconffile, nodeconfcontent)
  
  def loadnodeauth(self):
    nodeauthfile = self.pilot_dir + self.authfilename
    nodeauth = None
    try:
      nodeauth = json.loads(self.sbc.getFileContent(nodeauthfile))
    except:
      nodeauth = None
    return nodeauth

  def savenodeauth(self, nodeauth):
    nodeauthfile = self.pilot_dir + self.authfilename
    nodeauthcontent = json.dumps(nodeauth)
    return self.sbc.setFileContent(nodeauthfile, nodeauthcontent)

  def authenticate(self):

    # check if there is an node authfile on the host
    nodeauth = self.loadnodeauth()
    if nodeauth != None: #there is one, load
      self.tokenset = nodeauth
      self.decode()
      if self.decoded != None: # token was ok
        return

    payload = {'client_id': self.client_id, 'scope':'openid email offline_access', 'prompt': 'consent' }
    headers = { 'content-type': "application/x-www-form-urlencoded" }

    try:
      response = requests.post(self.oauth_device_code_url, data=payload, headers=headers).json()
    
      print("\n\n")
      print("Open {}{}{} and enter".format(Style.BRIGHT, response['verification_uri'], Style.NORMAL))
      print("\n\n")
      print("""=======>      {}{}{}       <=======""".format(Style.BRIGHT, response['user_code'], Style.NORMAL))
      print("\n\nor scan this code with your Camera app to skip entering the code")
      qrcode_terminal.draw(response['verification_uri_complete'])
      print("note: this code expires in {} minutes".format(response['expires_in'] / 60))

      payload2 = { 'grant_type': "urn:ietf:params:oauth:grant-type:device_code", 
                   'client_id': self.client_id, 'device_code': response['device_code'] }

      done = False
      interval = int(response['interval'])

      while (not done):
        response2 = requests.post(self.oauth_token_url, data=payload2, headers=headers).json()
        if 'error' in response2:
          if response2['error'] == 'authorization_pending':
            time.sleep(interval)
          elif response2['error'] == 'access_denied':
            print(Fore.RED + 'Flow cancelled')
            done = True
          elif response2['error'] == 'expired_token':
            print(Fore.RED + 'Token is expired')
            done = True
          else:
            print(Fore.RED + 'Error {}; {}'.format(response2['error'], response2['error_description']))
            done = True
        elif 'access_token' in response2:
          print(Fore.GREEN + "\n\nYour device was sucessfully authorized.")
          self.tokenset = response2
          self.decode()
          self.savenodeauth(response2)
          done = True

    except Exception as e: 
      print(Fore.RED + 'Error authenticating the device {}'.format(e))
      print(e)

  def refresh(self, decode=True):
    try:
      if self.tokenset != None and 'refresh_token' in self.tokenset:
        headers = { 'content-type': "application/x-www-form-urlencoded" }
        payload = { 'grant_type': "refresh_token", 
                    'client_id': self.client_id,
                    'refresh_token': self.tokenset['refresh_token']
                  }
        response = requests.post(self.oauth_token_url, data=payload, headers=headers).json()

        if 'access_token' in response:
          response['refresh_token'] = self.tokenset['refresh_token']
          self.tokenset = response
          with open(self.authfile, 'w') as authfile:
            json.dump(self.tokenset, authfile)
          if decode:
            self.decode()
          return True
    except:
      print(Fore.RED + 'Error getting refresh token {}'.format(e))
      print(e)

    return False
  
  def decode(self):
    self.decoded = None
    if self.tokenset != None and self.keys != None:
      try:
        pubkey = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(self.keys))
        self.decoded = jwt.decode(self.tokenset['access_token'], pubkey, algorithms='RS256', audience = self.audience) #, audience=self.config.CLIENT_ID) 
      except jwt.ExpiredSignatureError:
        try:
          self.refresh(False) # do not decode, might cause endless loop 
          self.decoded = jwt.decode(self.tokenset['access_token'], pubkey, algorithms='RS256', audience = self.audience) #, audience=self.config.CLIENT_ID) 
        except Exception as e: #hopeless, give up
          print(Fore.RED + 'error decoding token')
          print(e)
      except Exception as e:
        print(Fore.RED + 'error decoding token')
        print(e)
  
  def get_token(self):
    if self.tokenset == None:
      try:
        with open(self.authfile) as authfile:
          self.tokenset = json.load(authfile)
          self.decode()
      except:
        pass

    if self.decoded == None:
      self.authenticate()
    
    if self.decoded == None:
      print(Fore.RED + 'Error, cannot authenticate')
      exit(1)
    
    expires = int(self.decoded['exp'] - time.time())
    
    #print('expires in {} seconds ({} hours)'.format(expires, str(datetime.timedelta(seconds=expires))))

    if expires < 60: # expires in less than 60 seconds
      if not self.refresh():
        print(Fore.RED + 'Cannot refresh authentication token, please authenticate again')
        self.authenticate()
        if self.decoded == None:
          print(Fore.RED + 'Error, cannot authenticate')
          exit(1)

    # here we should have a valid access token
    return 'Bearer {}'.format(self.tokenset['access_token'])

  def query(self, query, variables=None, isPublic=False):
    transport = None
    if isPublic:
      transport = RequestsHTTPTransport( url=self.pilot_server, use_json=True )
    else:
      transport = RequestsHTTPTransport( url=self.pilot_server, use_json=True, headers={ 'Authorization': self.get_token() } )

    client = Client( transport=transport, fetch_schema_from_transport=True )
    return client.execute(query,  variable_values=variables)
    

  def getuserid(self):
    if self.decoded != None and 'https://hasura.io/jwt/claims' in self.decoded and 'x-hasura-user-id' in self.decoded['https://hasura.io/jwt/claims']:
      return int(self.decoded['https://hasura.io/jwt/claims']['x-hasura-user-id'])
    return -1

  def getnode(self):
    nodeid = None

    nodeconf = self.loadnodeconf()
    if nodeconf != None and 'nodeid' in nodeconf:
      nodeid = nodeconf["nodeid"]


    try:
      result = self.query(gql("""query getnode($nodeid: uuid) {
        pilot_node(where: {id: {_eq: $nodeid} }) {
            id
            name
            pilotconfig
            online
          }
      }
      """), {
        "nodeid": nodeid
      })
      if 'pilot_node' in result and isinstance(result['pilot_node'], list) and len(result['pilot_node']) == 1 and 'id' in result['pilot_node'][0]:
        return result['pilot_node'][0]

    except Exception as e:
      print('Error getting node from server')
      print(e)
    return None
  
  def updatenode(self, fwconfig, name='', description=''):
    try: 
      userid = self.getuserid()
      if userid <= 0:
        print(Fore.RED + "Not authenticated, cannot configure node.")
        return

      node = self.getnode()
      nodeid = node['id'] if node !=None else None

      if nodeid == None:
        nodeid = str(uuid4())
        nodeconf = { 'nodeid': nodeid }
        self.savenodeconf(nodeconf)
      if fwconfig == None:
        fwconfig = {}

      query = gql("""
        mutation upsertNode($nodeid: uuid, $userid: Int, $pilotconfig: jsonb, $name: String, $description: String) {
          insert_pilot_node(objects: {id: $nodeid, pilotconfig: $pilotconfig, name: $name, description: $description, userid: $userid}, 
            on_conflict: {constraint: node_pkey, update_columns: [pilotconfig]}) {
            affected_rows
          }
        }
      """)
      result = self.query(query, {
        "nodeid": nodeid,
        "userid": userid,
        "pilotconfig": fwconfig,
        "name": name,
        "description": description
      })

      if 'insert_pilot_node' in result and 'affected_rows' in result['insert_pilot_node'] and result['insert_pilot_node']['affected_rows'] == 1:
        print(Fore.GREEN + "Successfully updated node")

    except Exception as e:
      print(Fore.RED + 'could not update node')
      print(e)
  

  def registernode(self, fwconfig):

    name = input("Enter a name for this node: ")
    description = input("Enter a description for this node: ")

    self.updatenode(fwconfig, name, description)
  