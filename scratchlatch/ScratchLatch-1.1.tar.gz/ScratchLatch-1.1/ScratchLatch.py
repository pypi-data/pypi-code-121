import websocket
import requests
import logging
import json
import re
import os

try:
  ws = websocket.WebSocket()
except:
  os.system('pip install websocket-client')

class ScratchLatch():
    def __init__(self, username: str, password: str) -> None:
        self.chars = """AabBCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789 -_`~!@#$%^&*()+=[];:'"\|,.<>/?}{"""
        global uname
        uname = username
        self.username = username
        self.password = password
        self.headers = {
            "x-csrftoken": "a",
            "x-requested-with": "XMLHttpRequest",
            "Cookie": "scratchcsrftoken=a;scratchlanguage=en;",
            "referer": "https://scratch.mit.edu",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
        }
        try:
            data = json.dumps({
                "username": username,
                "password": password
            })
            request = requests.post(
                'https://scratch.mit.edu/login/', data=data, headers=self.headers)
            self.sessionId = re.search(
                '\"(.*)\"', request.headers['Set-Cookie']).group()
            self.token = request.json()[0]["token"]
            global sessionId
            sessionId = self.sessionId
            headers = {
                "x-requested-with": "XMLHttpRequest",
                "Cookie": "scratchlanguage=en;permissions=%7B%7D;",
                "referer": "https://scratch.mit.edu",
            }
            request = requests.get(
                "https://scratch.mit.edu/csrf_token/", headers=headers)
            self.csrftoken = re.search(
                "scratchcsrftoken=(.*?);", request.headers["Set-Cookie"]
            ).group(1)

        except AttributeError:
            raise Exception(
                'Error: Invalid credentials. Authentication failed.')
        else:
            self.headers = {
                "x-csrftoken": self.csrftoken,
                "X-Token": self.token,
                "x-requested-with": "XMLHttpRequest",
                "Cookie": "scratchcsrftoken="
                + self.csrftoken
                + ";scratchlanguage=en;scratchsessionsid="
                + self.sessionId
                + ";",
                "referer": "",
            }

    def decode(self, text):
        decoded = ""
        text = str(text)
        y = 0
        for i in range(0, len(text)//2):
            x = self.chars[int(str(text[y])+str(text[int(y)+1]))-1]
            decoded = str(decoded)+str(x)
            y += 2
        return decoded

    def encode(self, text):
        encoded = ""
        length = int(len(text))
        for i in range(0, length):
            try:
                x = int(self.chars.index(text[i])+1)
                if x < 10:
                    x = str(0)+str(x)
                encoded = encoded + str(x)
            except ValueError:
                logging.error('Character not supported')
        return encoded

    class project:

        def __init__(self, id: int) -> None:
            self.id = id

        def stats(self) -> dict:
            r = requests.get(
                "https://api.scratch.mit.edu/projects/"+str(self.id))
            data = r.json()
            return data['stats']

        def getComments(self) -> 'list[dict]':
            uname = requests.get(
                "https://api.scratch.mit.edu/projects/"+str(self.id)).json()
            if uname != {"code": "NotFound", "message": ""}:
                uname = uname['author']['username']
                data = requests.get("https://api.scratch.mit.edu/users/" +
                                    str(uname)+"/projects/"+str(self.id)+"/comments").json()
                comments = []
                if data != {"code": "ResourceNotFound", "message": "/users/"+str(uname)+"/projects/175/comments does not exist"} and data != {"code": "NotFound", "message": ""}:
                    x = ""
                    for i in data:
                        if "content" in i:
                            x = i['content']
                        else:
                            if "image" in i:
                                x = i['image']
                            else:
                                x = "None"
                        comments.append(
                            str('Username: '+str(uname))+(str(', Content: ')+str(x)))
                    return data

        def getInfo(self) -> dict:
            r = requests.get(
                'https://api.scratch.mit.edu/projects/'+str(self.id)
            ).json()
            return r

        def getAssets(self, type='img') -> 'list[str]':
            r = json.loads(requests.get(
                'https://projects.scratch.mit.edu/'+str(self.id)
            ).text.encode('utf-8'))

            assets = []
            for i in range(len(r['targets'])):
                if type == 'images':
                    assets.append('https://cdn.assets.scratch.mit.edu/internalapi/asset/' +
                                  str(r['targets'][i]['costumes'][0]['md5ext'])+'/get')
                elif type == 'sounds':
                    assets.append('https://cdn.assets.scratch.mit.edu/internalapi/asset/' +
                                  str(r['targets'][i]['sounds'][0]['md5ext'])+'/get')
            return assets

    class studioSession:
        def __init__(self, sid: int) -> None:
            self.headers = {
                "x-csrftoken": "a",
                "x-requested-with": "XMLHttpRequest",
                "Cookie": "scratchcsrftoken=a;scratchlanguage=en;",
                "referer": "https://scratch.mit.edu",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
            }
            self.sid = sid

        def invite(self, user: str) -> None:
            self.headers["referer"] = (
                "https://scratch.mit.edu/studios/" + str(self.sid) + "/curators/")
            requests.put("https://scratch.mit.edu/site-api/users/curators-in/" +
                         str(self.sid) + "/invite_curator/?usernames=" + user, headers=self.headers)

        def addProject(self, pid: int):
            self.headers['referer'] = "https://scratch.mit.edu/projects/" + \
                str(pid)
            return requests.post("https://api.scratch.mit.edu/studios/"+str(self.sid)+"/project/"+str(pid), headers=self.headers)

        def postComment(self, content: str, parent_id: str = "", commentee_id: str = ""):
            self.headers['referer'] = (
                "https://scratch.mit.edu/studios/" +
                str(self.sid) + "/comments/"
            )
            data = {
                "commentee_id": commentee_id,
                "content": content,
                "parent_id": parent_id,
            }
            return requests.post(
                "https://scratch.mit.edu/site-api/comments/gallery/"
                + str(self.sid)
                + "/add/",
                headers=self.headers,
                data=json.dumps(data),
            )

        def getComments(self) -> 'list[str]':
            r = requests.get(
                "https://api.scratch.mit.edu/studios/"+str(self.sid)+"/comments")
            data = r.json()
            comments = []
            for i in data:
                x = i['content']
                comments.append(x)
            return comments

        def follow(self) -> dict:
            self.headers['referer'] = "https://scratch.mit.edu/studios/" + \
                str(self.sid)
            return requests.put(
                "https://scratch.mit.edu/site-api/users/bookmarkers/"
                + str(self.sid)
                + "/remove/?usernames="
                + self.username,
                headers=self.headers,
            ).json()

        def unfollow(self) -> dict:
            self.headers['referer'] = "https://scratch.mit.edu/studios/" + \
                str(self.sid)
            return requests.put(
                "https://scratch.mit.edu/site-api/users/bookmarkers/"
                + str(id)
                + "/remove/?usernames="
                + self.username,
                headers=self.headers,
            ).json()

    class projectSession:

        def __init__(self, pid: int) -> None:
            self.headers = {
                "x-csrftoken": "a",
                "x-requested-with": "XMLHttpRequest",
                "Cookie": "scratchcsrftoken=a;scratchlanguage=en;",
                "referer": "https://scratch.mit.edu",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
            }
            self.pid = pid

        def share(self):
            self.headers["referer"] = (
                "https://scratch.mit.edu/projects/"+str(self.pid)
            )
            return requests.put("https://api.scratch.mit.edu/proxy/projects/"+str(self.pid)+"/share", headers=self.headers)

        def unshare(self):
            self.headers["referer"] = (
                "https://scratch.mit.edu/projects/"+str(self.pid)
            )
            return requests.put("https://api.scratch.mit.edu/proxy/projects/"+str(self.pid)+"/unshare", headers=self.headers)

        def favorite(self):
            self.headers['referer'] = "https://scratch.mit.edu/projects/" + \
                str(self.pid)
            return requests.post(
                "https://api.scratch.mit.edu/proxy/projects/"
                + str(self.pid)
                + "/favorites/user/"
                + self.username,
                headers=self.headers,
            ).json()

        def unfavorite(self):
            self.headers['referer'] = "https://scratch.mit.edu/projects/" + \
                str(self.pid)
            return requests.delete(
                "https://api.scratch.mit.edu/proxy/projects/"
                + str(self.pid)
                + "/favorites/user/"
                + self.username,
                headers=self.headers,
            ).json()

        def love(self):
            self.headers['referer'] = "https://scratch.mit.edu/projects/" + \
                str(self.pid)
            return requests.post(
                "https://api.scratch.mit.edu/proxy/projects/"
                + str(self.pid)
                + "/loves/user/"
                + self.username,
                headers=self.headers,
            ).json()

        def unlove(self):
            self.headers['referer'] = "https://scratch.mit.edu/projects/" + \
                str(self.pid)
            return requests.delete(
                "https://api.scratch.mit.edu/proxy/projects/"
                + str(self.pid)
                + "/loves/user/"
                + self.username,
                headers=self.headers,
            ).json()

        def remix(self):
            self.headers['referer'] = "https://scratch.mit.edu/projects/" + \
                str(self.pid)
            return requests.post("https://projects.scratch.mit.edu/?is_remix=1&original_id="+str(self.pid)+"&title=Scratch%20Project").json()

    class userSession:

        def __init__(self, username: str) -> None:
            self.headers = {
                "x-csrftoken": "a",
                "x-requested-with": "XMLHttpRequest",
                "Cookie": "scratchcsrftoken=a;scratchlanguage=en;",
                "referer": "https://scratch.mit.edu",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
            }
            self.username = uname
            self.uname2 = username

        def follow(self):
            self.headers['referer'] = "https://scratch.mit.edu/users/" + \
                str(self.username)+"/"
            return requests.put(
                "https://scratch.mit.edu/site-api/users/followers/"
                + self.username
                + "/add/?usernames="
                + self.uname2,
                headers=self.headers,
            ).json()

        def unfollow(self):
            self.headers['referer'] = "https://scratch.mit.edu/users/" + \
                str(self.username)+"/"
            return requests.put(
                "https://scratch.mit.edu/site-api/users/followers/"
                + self.username
                + "/remove/?usernames="
                + self.uname2,
                headers=self.headers,
            ).json()

        def toggleCommenting(self):
            self.headers['referer'] = "https://scratch.mit.edu/users/" + \
                str(self.username)
            return requests.post(
                "https://scratch.mit.edu/site-api/comments/user/" +
                str(self.username)+"/toggle-comments/",
                headers=self.headers,
            )

        def postComment(self, content: str, parent_id: str = "", commentee_id: str = ""):
            self.headers['referer'] = "https://scratch.mit.edu/users/" + self.uname2
            data = {
                'content': content,
                'parent_id': parent_id,
                'commentee_id': commentee_id
            }
            return requests.post("https://scratch.mit.edu/site-api/comments/user/" + self.uname2 + "/add/", data=json.dumps(data), headers=self.headers).json()

    class user:

        def __init__(self, user: str) -> None:
            self.user = user
            self.headers = {
                "x-csrftoken": "a",
                "x-requested-with": "XMLHttpRequest",
                "Cookie": "scratchcsrftoken=a;scratchlanguage=en;",
                "referer": "https://scratch.mit.edu",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
            }

        def exists(self) -> bool:
            return requests.get("https://api.scratch.mit.edu/accounts/checkusername/"+str(self.user)).json() == {"username": self.user, "msg": "username exists"}

        def messageCount(self):
            self.headers['referer'] = "https://scratch.mit.edu"
            return requests.get("https://api-9gr.vercel.app/scratch/messages/"+str(self.user), headers=self.headers).json()

        def getMessages(self) -> dict:
            return requests.get("https://api.scratch.mit.edu/users/"+str(self.user)+"/messages" + "/", headers=self.headers).json()

        def getStatus(self) -> str:
            return requests.get("https://api.scratch.mit.edu/users/"+str(self.user)).json()['profile']['status']

        def getBio(self) -> str:
            return requests.get("https://api.scratch.mit.edu/users/"+str(self.user)).json()['profile']['bio']

        def projects(self) -> 'dict[str, list]':
            r = requests.get(
                "https://api.scratch.mit.edu/users/"+str(self.user)+"/projects")
            data = r.json()
            titles = {}
            for i in data:
                x = i['title']
                y = i['id']
                z = i['history']['shared']
                titles[x] = [y, z]
            return titles
    class cloud:
      class scratch:
  
          def __init__(self, pid: int):
              global ws
              global PROJECT_ID
              self.username = uname
              PROJECT_ID = pid
              ws.connect('wss://clouddata.scratch.mit.edu', cookie='scratchsessionsid='+sessionId+';',
                         origin='https://scratch.mit.edu', enable_multithread=True)
              ws.send(json.dumps({
                  'method': 'handshake',
                  'user': self.username,
                  'project_id': str(pid)
              }) + '\n')
  
          def setVar(self, variable: str, value: str, showErrors=True) -> None:
              try:
                  ws.send(json.dumps({
                      'method': 'set',
                      'name': '☁ ' + variable,
                      'value': str(value),
                      'user': self.username,
                      'project_id': str(PROJECT_ID)
                  }) + '\n')
              except BrokenPipeError:
                  if showErrors:
                    logging.error('Broken Pipe Error. Connection Lost.')
                  ws.connect('wss://clouddata.scratch.mit.edu', cookie='scratchsessionsid='+sessionId+';',
                             origin='https://scratch.mit.edu', enable_multithread=True)
                  ws.send(json.dumps({
                      'method': 'handshake',
                      'user': self.username,
                      'project_id': str(PROJECT_ID)
                  }) + '\n')
                  logging.info('Re-connected to wss://clouddata.scratch.mit.edu')
                  logging.info('Re-sending the data')
                  ws.send(json.dumps({
                      'method': 'set',
                      'name': '☁ ' + variable,
                      'value': str(value),
                      'user': self.username,
                      'project_id': str(PROJECT_ID)
                  }) + '\n')
  
          def readVar(self, name: str, limit: str = "1000") -> str:
              try:
                  resp = requests.get("https://clouddata.scratch.mit.edu/logs?projectid=" +
                                      str(PROJECT_ID)+"&limit="+str(limit)+"&offset=0").json()
                  for i in resp:
                      x = i['name']
                      if x == ('☁ ' + str(name)):
                          return i['value']
              except Exception:
                  raise Exception('Cloud variable could not be read.')
  
      class turbowarp:
          def __init__(self, pid):
              global ws
              global turbowarpid
              self.username = uname
              turbowarpid = pid
              ws.connect('wss://clouddata.turbowarp.org',
                         origin='https://turbowarp.org', enable_multithread=True)
              ws.send(json.dumps({
                  'method': 'handshake',
                  'user': self.username,
                  'project_id': str(turbowarpid)
              }) + '\n')
  
          def setVar(self, variable, value):
              ws.send(json.dumps({
                  'method': 'set',
                  'name': '☁ ' + variable,
                  'value': str(value),
                  'user': self.username,
                  'project_id': str(turbowarpid)
              }) + '\n')
  
          def readVar(self, variable):
              ws.send(json.dumps({
                  'method': 'get',
                  'project_id': str(turbowarpid)
              }) + '\n')
              data = ws.recv()
              data = data.split('\n')
              result = []
              for i in data:
                  result.append(json.loads(i))
              for i in result:
                  if i['name'] == '☁ ' + variable:
                      return i['value']
              return 'Variable not found.'