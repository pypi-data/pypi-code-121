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

ICertificateSecurityMgmt_VERSION = "4.1.62053"

class ICertificateSecurityMgmt(BaseEndpoint):
    def __init__(self, apiKey, url ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/system/security/certificate'

    def renewLetsEncryptCertificate (self, uid , url , email ):
        postUri = "/_renew/{uid}";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}",uid);
        queryParams = {   'url': url  , 'email': email   };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICertificateSecurityMgmt_VERSION}, data = __encoded__);
        from netbluemind.core.task.api.TaskStatusState import TaskStatusState
        from netbluemind.core.task.api.TaskStatusState import __TaskStatusStateSerDer__
        return self.handleResult__(__TaskStatusStateSerDer__(), response)
