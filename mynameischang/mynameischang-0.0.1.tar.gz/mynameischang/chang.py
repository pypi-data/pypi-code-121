class Chang:
	'''
	คลาส Chang คือ
	ข้อมูลที่เกี่ยวกับ Chang
	ประกอบด้วยชื่อเพจ
	ชื่อช่องยูทูป

	Example
	#---------------------
	name = Chang()
	name.show_name()
	name.show_page()
	name.show_youtube()
	name.show_page()
	name.about()
	name.show_pic()
	#---------------------
	'''

	def __init__(self):
		self.name = 'ลุงช้าง'
		self.page = 'https://www.facebook.com'

	def show_name(self):
		print('สวัสดีฉันชื่อ {}'.format(self.name))

	def show_page(self):
		print('FB Page: {}'.format(self.name))

	def show_youtube(self):
		print('https://www.youtube.com')

	def about(self):
		text = '''
		*******************************
		สวัสดี นี่คือการทดสอบ การสร้าง library 
		   และสร้างตัวอย่าง class แบบง่ายๆ
		        <<โดย 'ลุงช้าง'>>
		*******************************
		'''
		print(text)


	def show_pic(self):
		pic = '''
				    _    _
				   /=\\""/=\\
				  (=(0_0 |=)__
				   \\_\\ _/_/   )
				     /_/   _  /\\
				     |/ |\\ || |
				       ~ ~  ~
				'''
		print(pic)


if __name__ == '__main__':
	name = Chang()
	name.show_name()
	name.show_page()
	name.show_youtube()
	name.show_page()
	name.about()
	name.show_pic()