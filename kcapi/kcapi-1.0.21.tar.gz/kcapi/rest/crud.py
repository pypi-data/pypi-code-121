import requests, json
from .resp import ResponseHandler

class KeycloakCRUD(object):
    @staticmethod
    def get_child(that, resource_id, resource_name):
        kc = KeycloakCRUD()
        kc.token = that.token
        kc.targets = that.targets.copy()

        kc.targets.addResources([resource_id, resource_name])

        return kc

    def __init__(self): 
        self.targets = None
        self.token = None

    def headers(self):

        if self.token.expired():
            self.token = self.token.refresh()

        return {
                'Content-type': 'application/json', 
                'Authorization': 'Bearer '+ self.token.get_token()
        }

    def setIdentifier(self, _id = None, url = None):
        if _id:
            return url.addResource(_id)
        else:
            return url
    
    def create(self, payload):
        url = self.targets.url('create')

        ret = requests.post(url, data=json.dumps(payload), headers=self.headers())
        return ResponseHandler(url, method='Post', payload=payload).handleResponse(ret)

    def update(self, obj_id=None, payload=None):
        url = self.targets.url('update')
        target = str(self.setIdentifier(obj_id, url))

        ret = requests.put(target, data=json.dumps(payload), headers=self.headers())
        return ResponseHandler(target, method='Put', payload=payload).handleResponse(ret)

    def remove(self, _id):
        delete = self.targets.url('delete')
        url = self.setIdentifier(_id, delete)
        ret = requests.delete(url, headers=self.headers())
        return ResponseHandler(url, method='Delete').handleResponse(ret)
        
    def get(self, _id):
        url = self.targets.url('read')
        ret = requests.get(str(self.setIdentifier(_id, url)), headers=self.headers())
        return ResponseHandler(url, method='Get').handleResponse(ret)

    def findAll(self):
        url = self.targets.url('read')
        ret = requests.get(url, headers=self.headers())
        return ResponseHandler(url, method='Get').handleResponse(ret)

    def findFirst(self, params):
        return self.findFirstByKV(params['key'], params['value'])

    def findFirstByKV(self, key, value):
        rows = self.findAll().verify().resp().json()

        for row in rows: 
            if row[key].lower() == value.lower():
                return row

        return []

    def all(self):
        return self.findAll().verify().resp().json()

    def updateUsingKV(self, key, value, obj): 
        res_data = self.findFirstByKV(key,value)

        if res_data: 
            data_id = res_data['id']
            res_data.update(obj)
            return self.update(data_id, res_data).isOk() 
        else:
            return False

    def removeFirstByKV(self, key, value, custom_key="id"):
        row = self.findFirstByKV(key,value)

        if row:
            return self.remove(row[custom_key]).isOk()
        else:
            return False

    def existByKV(self, key, value): 
        ret = self.findFirstByKV(key, value)
        return ret != False

    def exist(self, _id):
        return self.get(_id).ok()


