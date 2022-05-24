import json
import rfc3339
from datetime import datetime
import time
import pytz
class InstanceInfo:
    def __init__(self,name="stat-api",startupAt=None,version_file=None):
        self.name=name
        self.startupAt=startupAt
        self.date = startupAt
        with open(version_file) as ss:
            s = json.load(ss)
        self.info=s

    def toMap(self):
        dt = datetime.now(pytz.UTC)
        return {"name": self.name,"startupAt": self.startupAt.strftime("%Y-%m-%dT%H:%M:%SZ"),"date":dt.strftime("%Y-%m-%dT%H:%M:%SZ"),"info":self.info}

#zookeeper中service的注册信息
"""
Ex. :
{
    "uriSpec": {
        "parts": [
            {
                "variable": true,
                "value": "scheme"
            },
            {
                "variable": false,
                "value": "://"
            },
            {
                "variable": true,
                "value": "address"
            },
            {
                "variable": false,
                "value": ":"
            },
            {
                "variable": true,
                "value": "port"
            }
        ]
    },
    "serviceType": "DYNAMIC",
    "registrationTimeUTC": 1546512992955,
    "port": 80,
    "payload": {
        "name": "iauth",
        "metadata": {
            "git.total.commit.count": "117",
            "git.tags": "v1.5.1",
            "git.remote.origin.url": "https://gitlab.inhand.local/elements/iauth",
            "git.commit.user.name": "j3r0lin",
            "git.commit.user.email": "j3r0lin@icloud.com",
            "git.commit.time": "2018-12-24T09:27:47Z",
            "git.commit.message.short": "DM-243 allow create user by phone number",
            "git.commit.message.full": "DM-243 allow create user by phone number",
            "git.commit.id.full": "7cec61d6797a897786ed087832dc58f70a3ef2fe",
            "git.commit.id.abbrev": "7cec61d",
            "git.closest.tag.name": "v1.5.1",
            "git.build.version": "v1.5.1",
            "git.build.time": "2018-12-24T10:53:31Z",
            "git.branch": "v1.5.1",
            "build.version": "v1.5.1",
            "build.time": "2018-12-24T10:53:31Z",
            "build.name": "iauth",
            "build.artifact": "iauth"
        },
        "id": "iauth:80",
        "@class": "org.springframework.cloud.zookeeper.discovery.ZookeeperInstance"
    },
    "name": "iauth",
    "id": "b89ddcfa-61cb-44da-8a21-29e13c06d801",
    "address": "172.18.0.3"
}
"""
class ServiceInfo:
    def __init__(self,id="",name="",address="0.0.0.0",port=80,serviceType="DYNAMIC",metadata={},class_desc="org.springframework.cloud.zookeeper.discovery.ZookeeperInstance"):
        self.uriSpec={"parts":[{
                "variable": True,
                "value": "scheme"
            },
            {
                "variable": False,
                "value": "://"
            },
            {
                "variable": True,
                "value": "address"
            },
            {
                "variable": False,
                "value": ":"
            },
            {
                "variable": True,
                "value": "port"
            }]}
        self.serviceType=serviceType
        self.registraionTimeUTC= int(time.mktime(datetime.now().timetuple()))
        self.port= port
        self.address=address
        self.id=id
        self.name=name
        self.metadata=metadata
        self.class_desc=class_desc

    def toMap(self):
        return {"id":self.id,"name":self.name,"address":self.address,"serviceType":self.serviceType,"registrationTimeUTC":self.registraionTimeUTC,
                "port":self.port,"uriSpec":self.uriSpec,"sslPort":None,"payload":{"name":self.name,"id":self.id,"@class":self.class_desc,"metadata":self.metadata}}


class ApisInfo:
    def __init__(self,url="",weight=100,id="",name="",apis=[]):
        self.url=url
        self.weight=weight
        self.name=name
        self.id=id
        self.apis=apis

    def toMap(self):
        return {"id":self.id,"name":self.name,"server":{"url":self.url,"weight":self.weight},"apis":self.apis}