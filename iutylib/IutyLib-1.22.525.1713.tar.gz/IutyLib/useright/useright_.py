from IutyLib.database.mysql import MySql
from IutyLib.database.dbbase import *

from flask import session,request,redirect,url_for,send_from_directory
from flask_restful import Resource

mysql = MySql('localhost','root','fastcorp','iuwork')

class UseRight(mysql.Model):
    uid = Column(type = str,Length = 12,IsIndex = True)
    aid = Column(type = str,Length = 40,IsIndex = True)
    right = Column()
    pass
    
class UseRightApi(Resource):
    def check():
        db = UseRight()
        db.check()
        pass
    
    def getAidList():
        uid = session.get("uid")
        rtn = {'success':False}
        if uid:
            db = UseRight()
            aids = db.query(target=r'`aid`,`right`',where=r"uid = '{}'".format(uid))
            rtn['success'] = True
            rtn['useright'] = aids
            return rtn
        else:
            rtn['error'] = 'user is not log in'
            return rtn
        pass
    
    

    def post(self):
        cmd = request.form.get('cmd')
        return UseRightApi.getAidList()
    

if __name__ == '__main__':
    #print(UseRightApi.__doc__)
    pass
