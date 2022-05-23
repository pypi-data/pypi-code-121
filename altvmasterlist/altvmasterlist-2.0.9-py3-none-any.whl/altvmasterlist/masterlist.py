#!/usr/bin/env python3

from urllib.request import urlopen, Request
from json import dumps, loads, decoder
from re import compile
import logging
import ssl

# Masterlist API Docs: https://docs.altv.mp/articles/master_list_api.html

# This is the config object for this package
# Here can you configure stuff like the api endpoint or the url format
class config:
    base_link = "https://api.altv.mp"
    all_server_stats_link = f"{base_link}/servers"
    all_servers_link = f"{base_link}/servers/list"
    server_link = f"{base_link}/server" + "/{}"
    server_average_link = f"{base_link}/avg" + "/{}/{}"
    server_max_link = f"{base_link}/max" + "/{}/{}"

logging.debug(f'starting with base link: {config.base_link}')

# This is the server object 
class Server:
    # initialize the object whith all values that are avalible in the alt:V masterlist API
    def __init__(self, active, id, maxPlayers, players, name, locked, host, port, gameMode, website, language, description, verified, promoted, useEarlyAuth, earlyAuthUrl, useCdn, cdnUrl, useVoiceChat, tags, bannerUrl, branch, build, version, lastUpdate):
        self.active = active
        self.id = id
        self.maxPlayers = maxPlayers
        self.players = players
        self.name = name
        self.locked = locked
        self.host = host
        self.port = port
        self.gameMode = gameMode
        self.website = website
        self.language = language
        self.description = description
        self.verified = verified
        self.promoted = promoted
        self.useEarlyAuth = useEarlyAuth
        self.earlyAuthUrl = earlyAuthUrl
        self.useCdn = useCdn
        self.cdnUrl = cdnUrl
        self.useVoiceChat = useVoiceChat
        self.tags = tags
        self.bannerUrl = bannerUrl
        self.branch = branch
        self.build = build
        self.version = version
        self.lastUpdate = lastUpdate

    # return the current server data as JSON object
    def get_json(self):
        return {
            "active": self.active,
            "id": self.id,
            "maxPlayers": self.maxPlayers,
            "players": self.players,
            "name": self.name,
            "locked": self.locked,
            "host": self.host,
            "port": self.port,
            "gameMode": self.gameMode,
            "website": self.website,
            "language": self.language,
            "description": self.description,
            "verified": self.verified,
            "promoted": self.promoted,
            "useEarlyAuth": self.useEarlyAuth,
            "earlyAuthUrl": self.earlyAuthUrl,
            "useCdn": self.useCdn,
            "cdnUrl": self.cdnUrl,
            "useVoiceChat": self.useVoiceChat,
            "tags": self.tags,
            "bannerUrl": self.bannerUrl,
            "branch": self.branch,
            "build": self.build,
            "version": self.version,
            "lastUpdate": self.lastUpdate
        }

    # fetch the server data and replace it
    def update(self):
        temp_server = get_server_by_id(self.id)
        # check if the function get_server_by_id() returned something
        if (temp_server == None):
            # set the server to be offline and the players to 0, because the server is offline or does not exist
            self.active = False
            self.players = 0
            return 

        # check if the server is online
        if (temp_server.active != False):
            # these values are only avalible when the server is online
            self.active = temp_server.active
            self.maxPlayers = temp_server.maxPlayers
            self.players = temp_server.players
            self.name = temp_server.name
            self.locked = temp_server.locked
            self.host = temp_server.host
            self.port = temp_server.port
            self.gameMode = temp_server.gameMode
            self.website = temp_server.website
            self.language = temp_server.language
            self.description = temp_server.description
            self.verified = temp_server.verified
            self.promoted = temp_server.promoted
            self.useEarlyAuth = temp_server.useEarlyAuth
            self.earlyAuthUrl = temp_server.earlyAuthUrl
            self.useCdn = temp_server.useCdn
            self.cdnUrl = temp_server.cdnUrl
            self.useVoiceChat = temp_server.useVoiceChat
            self.tags = temp_server.tags
            self.bannerUrl = temp_server.bannerUrl
            self.branch = temp_server.branch
            self.build = temp_server.build
            self.version = temp_server.version
            self.lastUpdate = temp_server.lastUpdate
        else:
            # set the server to be offline and the players to 0, because the server is offline
            self.active = False
            self.players = 0

    # use this function to fetch the server connect json
    # this file has every resource of the server with a hash and name
    def fetchconnectjson(self):
        if (self.useCdn == False):
            # This Server is not using a CDN.
            return None
        else:
            try:
                # lets try to get the connect json
                return request(self.cdnUrl + "/connect.json")
            except:
                # maybe the CDN is offline
                return None

def request(url):
    # Use the User-Agent: AltPublicAgent, because some servers protect their CDN with a simple User-Agent check e.g. https://luckyv.de does that
    request = Request(
        url, 
        data=None, 
        headers={
            'User-Agent': 'AltPublicAgent'
        }
    )

    with urlopen(request, context = ssl.create_default_context()) as response:
        if (response.status != 200):
            return None

        return loads(response.read().decode('utf-8'))

# Fetch the stats of all servers that are currently online
# e.g. {"serversCount":121,"playersCount":1595}
def get_server_stats():
    try:
        data = request(config.all_server_stats_link)
        return data
    except:
        return None
    
# Get all Servers that are online as Server object
def get_servers():
    return_servers = []
    try:
        servers = request(config.all_servers_link)
    except:
        return None
    
    if (servers == None or servers == "{}"):
        # if there are no servers return None
        return None
    for server in servers:
        # Now change every JSON response to a server object that we can e.g. update ourself
        temp_server = Server("unknown", server["id"], server["maxPlayers"], server["players"], server["name"], server["locked"], server["host"], server["port"], server["gameMode"], server["website"], server["language"], server["description"], server["verified"], server["promoted"], server["useEarlyAuth"], server["earlyAuthUrl"], server["useCdn"], server["cdnUrl"], server["useVoiceChat"], server["tags"], server["bannerUrl"], server["branch"], server["build"], server["version"], server["lastUpdate"])
        return_servers.append(temp_server)
        
    return return_servers

# get a single server by their server id
def get_server_by_id(id):
    try:
        temp_data = request(config.server_link.format(id))
    except:
        return Server(False, id, 0, 0, "", False, "", 0, "", "", "", "", False, False, False, "", False, "", False, "", "", "", 0, 0, "")
            
    if (temp_data == {} or temp_data == None):
        # the server just returned nothing: that should not happen!
        return Server(False, id, 0, 0, "", False, "", 0, "", "", "", "", False, False, False, "", False, "", False, "", "", "", 0, 0, "")
    else:
        if (temp_data["active"] == False):
            return Server(False, id, 0, 0, "", False, "", 0, "", "", "", "", False, False, False, "", False, "", False, "", "", "", 0, 0, "")
        else:
            # Create a Server object with the data and return that
            return Server(temp_data["active"], id, temp_data["info"]["maxPlayers"], temp_data["info"]["players"], temp_data["info"]["name"], temp_data["info"]["locked"], temp_data["info"]["host"], temp_data["info"]["port"], temp_data["info"]["gameMode"], temp_data["info"]["website"], temp_data["info"]["language"], temp_data["info"]["description"], temp_data["info"]["verified"], temp_data["info"]["promoted"], temp_data["info"]["useEarlyAuth"], temp_data["info"]["earlyAuthUrl"], temp_data["info"]["useCdn"], temp_data["info"]["cdnUrl"], temp_data["info"]["useVoiceChat"], temp_data["info"]["tags"], temp_data["info"]["bannerUrl"], temp_data["info"]["branch"], temp_data["info"]["build"], temp_data["info"]["version"], temp_data["info"]["lastUpdate"])

# get the average player count with a specified time range
# returns a JSON object e.g. [{"t":1652096100,"c":50},{"t":1652096400,"c":52},{"t":1652096700,"c":57}]
# time: 1d, 7d, 31d
def get_server_by_id_avg(id, time):
    try:
        return request(config.server_average_link.format(id, time))
    except:
        return None
    
# works like get_server_by_id_avg() but returns a integer/number
# time: 1d, 7d, 31d
def get_server_by_id_avg_result(id, time):
    try:
        response = get_server_by_id_avg(id, time)
    except:
        return None

    if (response == None):
        return None

    players_all = 0
    for entry in response:
        players_all = players_all + entry["c"]
    result = players_all / len(response)
    return round(result)

# get the maximum player count with a specified time range
# returns a JSON object e.g. [{"t":1652096100,"c":50},{"t":1652096400,"c":52},{"t":1652096700,"c":57}]
# time: 1d, 7d, 31d
def get_server_by_id_max(id, time):
    try:
        return request(config.server_max_link.format(id, time))
    except:
        return None

# validate agiven alt:V server id
def validate_id(id):
    regexraw = r"^[0-9a-zA-Z]{32}$"
    regex = compile(regexraw)
    result = regex.match(id)
    if (result != None):
        return True
    else:
        return False

if __name__ == "__main__":
    exit()