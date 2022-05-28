class Mac:
	"""
	class Mac คือ
	ข้อมูลเกี่ยวกับ Mac
	"""
	def __init__(self):
		self.name = 'Mac'
		self.page = 'https://www.facebook.com/MacNIDA'
	def show_name(self):
		print(f'Hello my name is {self.name}')

	def show_page(self):
		print(f'Hello my page is {self.page}')
	def about(self):
		text = """
		สวัสดีครับ ผมชื่อ แมค
		ทำงานที่ AOT
		"""
		print(text)
	def art(self):
		art = """
		    ________
    o      |   __   |
      \_ O |  |__|  |
   ____/ \ |___WW___|
   __/   /     ||
               ||
               ||
_______________||________________

"""
		print(art)

if __name__ == '__main__':
	mac = Mac()
	mac.show_name()
	mac.show_page()
	mac.about()
	mac.art()

