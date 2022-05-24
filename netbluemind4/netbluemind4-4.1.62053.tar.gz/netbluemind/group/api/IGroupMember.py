#
#  BEGIN LICENSE
#  Copyright (c) Blue Mind SAS, 2012-2016
# 
#  This file is part of BlueMind. BlueMind is a messaging and collaborative
#  solution.
# 
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of either the GNU Affero General Public License as
#  published by the Free Software Foundation (version 3 of the License).
# 
# 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# 
#  See LICENSE.txt
#  END LICENSE
#
import requests
import json
from netbluemind.python import serder
from netbluemind.python.client import BaseEndpoint

IGroupMember_VERSION = "4.1.62053"

class IGroupMember(BaseEndpoint):
    def __init__(self, apiKey, url ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +''

    def memberOf (self, uid ):
        postUri = "/{uid}/groups";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}",uid);
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IGroupMember_VERSION}, data = __encoded__);
        from netbluemind.group.api.Group import Group
        from netbluemind.group.api.Group import __GroupSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__GroupSerDer__())), response)
    def memberOfGroups (self, uid ):
        postUri = "/{uid}/groupUids";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}",uid);
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IGroupMember_VERSION}, data = __encoded__);
        return self.handleResult__(serder.ListSerDer(serder.STRING), response)
