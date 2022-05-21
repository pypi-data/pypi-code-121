#cheese

import re

from Cheese.cheeseController import CheeseController as cc
from Cheese.database import Database
from Cheese.metadata import Metadata

class Security:

    @staticmethod
    def authenticate(server, path):
        if (not Metadata.authentication["enabled"]):
            return True

        role = None
        dict = None
        if (server.headers.get("Authorization") != None):
            auth = Metadata.decode64(server.headers.get("Authorization"))

            for tp in Metadata.authentication["types"]:
                dict = Security.fitPatern(auth, tp["patern"])
                if (dict != None):

                    valid = Security.validate(dict, tp["validation"])
                    if (valid):
                        role = Security.findRole(dict, tp["roleId"])
                    break
        
        pth = cc.getPath(path)
        if (pth in Metadata.access.keys()):
            if (role == None):
                return False
            
            acc = Metadata.access[pth]
            if (role["value"] > acc["minRoleId"]):
                return False            

        return {
            "role": role,
            "login": dict
        }

    @staticmethod
    def findRole(dict, roleIdSql):
        for key in dict.keys():
            roleIdSql = roleIdSql.replace(f"${key}$", f"'{dict[key]}'")

        db = Database()
        response = db.query(roleIdSql)
        db.done()
        roleId = str(response[0][0])

        if (roleId not in Metadata.roles):
            return None
        return Metadata.roles[roleId]

    @staticmethod
    def validate(dict, validation):
        for key in dict.keys():
            validation = validation.replace(f"${key}$", f"'{dict[key]}'")

        db = Database()
        response = db.query(f"select case when exists ({validation}) then cast(1 as bit) else cast(0 as bit) end")
        db.done()
        return bool(response[0][0])

    @staticmethod
    def fitPatern(auth, patern):
        p = re.search(patern, auth)
        if (p == None): return None
        return p.groupdict()
