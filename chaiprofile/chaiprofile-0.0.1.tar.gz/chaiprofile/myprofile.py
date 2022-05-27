# myprofile.py

class Profile:
	''' 
	Example

	my = Profile('Chai')
	my.company = 'aerothai'
	my.hobby = ['Studying','Reading','Sleeping']
	print(my.name)
	my.show_email()
	my.show_myart()
	my.show_hobby()
	
	'''


	def __init__(self,name):  # ตัวแปรที่จองไว้ สำหรับอ้างถึงตัวแปรที่จะสร้างขึ้นมา
		self.name = name
		self.company = ''
		self.hobby = []
		self.art = '''
		     _                  _
		    | '-.            .-' |
		    | -. '..\\,.//,.' .- |
		    |   \  \\\||///  /   |
		   /|    )M\/%%%%/\/(  . |\
		
		  (//M   \%\\\%%//%//   M\\)
		(// M________ /\ ________M \\)
		 (// M\ \(',)|  |(',)/ /M \\) \\\\  
		  (\\ M\.  /,\\//,\  ./M //)
		    / MMmm( \\||// )mmMM \  \\
		     // MMM\\\||///MMM \\ \\
		      \//''\)/||\(/''\\/ \\
		      mrf\\( \oo/ )\\\/\
		         	'''

	def show_email(self):
		if self.company != '':
			print('{}@{}.com'.format(self.name.lower(),self.company))
		else:
			print('{}@gmail.com'.format(self.name.lower())) # lower = ตัวอักษรตัวเล็ก
	
	def show_myart(self):
		print(self.art)

	def show_hobby(self):
		if len(self.hobby) !=0:  # นับจำนวน ใน list hobby != ไม่เท่ากับ
			print('-----my hobby-----')
			for i,h in enumerate(self.hobby,start=1):  # run for loop ใส่ลำดับ ด้วย enmerate
				print(i,h)
			print('------------------')
		else:
			print('No hobby')


if __name__ == '__main__':  #ใช้เพื่อการทดสอบโปรแกรมใน file นี้เท่านั้น
	my = Profile('Chai')
	my.company = 'aeroth'
	my.hobby = ['Studying','Reading','Sleeping']
	print(my.name)
	my.show_email()
	my.show_myart()
	my.show_hobby()

	# help(my)