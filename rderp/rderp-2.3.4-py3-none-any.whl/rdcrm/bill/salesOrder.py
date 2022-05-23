from requests import  *
from login import Client
class SalesOrder(Client):
	def __init__(self):
		#明确继承自上一级
		#也可以不写默认继承
		Client.__init__(self)
	def query(self,fieldvalue='XSDD6'):
		res = Client.query(self,module='SalesOrder',fieldname='salesorder_no',fieldvalue=fieldvalue,url="/crmapi/crmoperation.php")
		return(res)
	def queryByNumber(self,fieldvalue='XSDD6'):
		res = Client.query(self,module='SalesOrder',fieldname='salesorder_no',fieldvalue=fieldvalue,url="/crmapi/crmoperation.php")
		return(res)
if __name__ =='__main__':
	so = SalesOrder()
	print(so)
	data2 = so.query()
	print(data2)

