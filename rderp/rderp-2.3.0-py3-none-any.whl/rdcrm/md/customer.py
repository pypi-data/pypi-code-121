from requests import  *
from login import Client
class Customer(Client):
	def __init__(self):
		#明确继承自上一级
		#也可以不写默认继承
		Client.__init__(self)
	def data_template(self):
		self.data = {
		"module" : "Accounts",
		"func" : "savebill",
		"apikey" : '',
		"token" : '',
		"username" : '',
		"account_no" : "test.01",  #客户编码
		"accountname" : "API新增客户_0002",				#客户名称
		'rating':'在投客户',     			#客户状态
		'leadsource':'source',     		#客户来源
		'nextcontactdate':'',				#下次回访日期
		"lastname" : "API新增联系人张三",				#联系人姓名
		"mobile" : "13761640839"			#联系人手机
		}
		return(self.data)
	def demo(self):
		self.save(self.data)

	def save(self,data):
		Client.save(self,data,url="/crmapi/crmoperation.php")
	def query(self,fieldvalue='苏州'):
		res = Client.query(self,module='Accounts',fieldname='accountname',fieldvalue=fieldvalue,url="/crmapi/crmoperation.php")
		return(res)
	def queryByNumber(self,fieldvalue='test.01'):
		res = Client.query(self,module='Accounts',fieldname='account_no',fieldvalue=fieldvalue,url="/crmapi/crmoperation.php")
		return(res)

	def queryByName(self, fieldvalue='苏州'):
		res = self.query(fieldvalue=fieldvalue)
		return(res)


if __name__ =='__main__':
	cus = Customer()
	print(cus)
	data_demo = cus.data_template()
	cus.save(data=data_demo)
	cus.demo()
	data2 = cus.query(fieldvalue='上海')
	print(data2)
	data3 = cus.queryByNumber()
	print(data3)
	data4 = cus.queryByName(fieldvalue='苏州')
	print(data4)

