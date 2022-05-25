#coding=utf-8
import http.client
import json
import sys
sys.path.append('../../')
from inhand.utilities.URLUtility import GenericURL

class SpringCloudSettings:
    def __init__(self):
        self.name=None
        self.profile=[]
        self.label=None
        self.version=None
        self.state=None
        self.params={}
        self.common={}

    def fetch_settings(self,config_url="http://10.5.16.213:8801/tube-stat-api/dev",module="tube-stat-api",profile="dev"):

        url = GenericURL(config_url)
        resource = ("%s" % url.path)
        if url.scheme == 'http':
            conn = http.client.HTTPConnection(url.host)  # httplib.HTTPConnection(host=self.url.host,timeout=30)
        else:
            conn = http.client.HTTPSConnection(url.host)  # httplib.HTTPSConnection(host=self.url.host,timeout=30)

        data=dict()
        print("Access %s" % config_url)
        conn.request("GET",resource)
        ret = conn.getresponse()

        s = json.loads(ret.read())
        self.__readSettings(s,module,profile)

    #for testing on ci server
    def readLocalSettings(self,path="../../../test.json",module="tube-stat-api", profile="dev"):
        with open(path) as f:
            s = json.load(f, encoding='utf-8')
        self.__readSettings(s,module,profile)


    def __readSettings(self,s,module="tube-stat-api", profile="dev"):
        self.name = s['name']
        self.profile=s['profiles']
        self.label = s['label']
        self.version=s['version']
        self.state=s['state']

        isPrivate = False
        filename = module +"-"+profile
        print('****************** filename: {} ********************'.format(filename))
        for item in s['propertySources']:
            if filename in item['name']:
                isPrivate = True
            else:
                isPrivate = False
            for k in item['source']:
                if k not in self.params.keys():
                    self.params[k] = item['source'][k]
                else:
                    if isPrivate:
                        self.params[k] = item['source'][k]


    def fetchArraySize(self,key_regex):
        size = 0
        key=key_regex.format(size)
        while key in self.params:
            size=size+1
            key=key_regex.format(size)
        return size

class Mongo:
    def __init__(self,params):
        prefix = 'spring.data.mongodb.%s'
        self.host = params[(prefix % ('host'))]
        self.port = params[(prefix % ('port'))]
        self.auth_mechanism =params[(prefix % ('authMechanism'))]
        self.auth_db = params[(prefix % ('authentication-database'))]
        self.account = params[(prefix % ('username'))]
        self.password=params[(prefix % ('password'))]

class RDB_JDBC:
    def __init__(self,params):
        prefix = 'spring.database.%s'
        #'jdbc:mysql://mysql:3306/iwos-app-ai'
        url=params[(prefix % ('url'))]
        args=url.split(':')
        self.type=args[1]
        self.host = args[2][2:]
        strs=args[3].split('/')
        self.port = int(strs[0])
        strs1=strs[1].split('?')
        self.database=strs1[0]
        self.account = params[(prefix % ('username'))]
        self.password=params[(prefix % ('password'))]

class Zk:
    def __init__(self,params):
        prefix = "spring.cloud.zookeeper.%s"
        self.url = params[(prefix % ('connect-string'))]
        self.path = params[(prefix % ('discovery.root'))]

"""
"config.mq.host": "rabbit",
"config.mq.account": "admin",
"config.mq.password": "1qaz2wsx",
"config.mq.port": 5672,
"""

class MQ:
    def __init__(self,params):
        prefix = "spring.rabbitmq.%s"
        self.host = params[(prefix % ('host'))]
        self.port = int(params[(prefix % ('port'))])
        self.account = params[(prefix % ('username'))]
        self.password = params[(prefix % ('password'))]


# class RDB:
#     def __init__(self,params):
#         prefix = "config.app.settings.database.%s"
#         self.type = params[(prefix % ('type'))]
#         self.database = params[(prefix % ('database'))]
#         self.host = params[(prefix % ('host'))]
#         self.port = int(params[(prefix % ('port'))])
#         self.account = params[(prefix % ('account'))]
#         self.password = params[(prefix % ('pawssword'))]


"""
"spring.redis.host": "10.5.0.27",
"spring.redis.port": 6379,
"spring.redis.database": 0,
"spring.redis.password": "1qaz2wsx",
"spring.redis.pool.max-active": 8,
"spring.redis.pool.max-wait": -1,
"spring.redis.pool.max-idle": 9,
"spring.redis.pool.min-idle": 0,
"spring.redis.timeout": 0,
"""
class Redis:
    def __init__(self, params):
        prefix = 'spring.redis.%s'
        self.host=params[(prefix % ('host'))]
        self.port=int(params[(prefix % ('port'))])
        self.database=int(params[(prefix % ('database'))])
        self.password=params[(prefix % ('password'))]
        key=(prefix % ('timeout'))
        self.timeout=0 if key not in params.keys() else  int(params[key])




