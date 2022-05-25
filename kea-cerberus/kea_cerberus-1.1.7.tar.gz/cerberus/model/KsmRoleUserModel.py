from cerberus.model.AbstractModelResource import AbstractModelResource
from cerberus.entities.entities import KsmRoleUser

class KsmRoleUserModel(AbstractModelResource):

    def __init__(self, url):
        super(KsmRoleUserModel,self).__init__(url)
        self.url = url
    

    def getRoleByUserId(self,userId):
        role = self.session.query(KsmRoleUser).filter(KsmRoleUser.user_id==userId).first()

        if role is not None:
            return role
        else:
            print("Throw Exception")
