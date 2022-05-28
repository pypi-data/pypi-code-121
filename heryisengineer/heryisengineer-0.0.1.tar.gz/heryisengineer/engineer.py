class HeryIsEngineer():
	"""
	ຄລາສ HeryIsEngineer ແມ່ນ
	ຂໍ້ມູນທີ່ກ່ຽວຂ້ອງກັບ  ເຫີຍ
	ປະກອບດ້ວຍຊື່ Page
	ຊື່ຊ່ອງ YouTube

	Example

	# ----------------------------
	
	myname = HeryIsEngineer()
	myname.show_name()
	myname.show_facebook_page()
	myname.about()
	myname.show_art()
	# ----------------------------
	"""

	def __init__(self):
		self.name = 'Hery Engineer'
		self.page = 'https://www.facebook.com/herytwenty.phonsavad'

	def show_name(self):
		print('ສະບາຍດີຂ້ອຍຊື່ {}'.format(self.name))

	def show_facebook_page(self):
		print('Facebook Page : {}'.format(self.page))

	def about(self):
		text = """
		ນີ້ແມ່ນຂໍ້ມູນສ່ວນໂຕຂອງຂ້ອຍ, Facebook ແລະ Page  
		"""
		print(text)

	def show_art(self):
		text = '''
				            _.._           
		     __.--"" __ ""--.__    
		   .'//   .-"  "-.   \\`,  
		  : :'  .'.  :;  ,`.  `; ; 
		 /; ;  /  T. $$ ,P  \\  : : 
		/: :  ;    T.:;,P    :  ; ;
		)| | :      `  '      ; | |
		`j | :.--------------.: | |
		 ; ; |                | : :
		 ; ; |                | : :
		 | | |                | | |
		 | | |                | | |
		 : : |                | ; ;
		 : : :________________: ; ;
		  ; ;__    _...._    __: : 
		  | ;  "-./ ,--, \\,-"  : | 
		  | '._   \\ ;  : /   _.' | 
		  :  __`-. `."",' .-'__  ; 
		   ;`.__> `.J__L.' <__.':  
		   ;.--._   .--.   _.--,:  
		   |`.__.' `.__.' `.__.'|  
		   |.--._   .--.   _.--,|  
		   |`.__.' `.__.' `.__.'|  
		   |.--._   .--.   _.--,|  
		   ;`.__.' `.__.' `.__.':  
		  : .--._   .--.   _.--, ; 
		  ; `.__.' `.__.' `.__.' : 
		  ;                      : 
		  '--..__          __..--' 
		         """"""""""       bug
		'''
		print(text)


if __name__ == '__main__':
	myname = HeryIsEngineer()
	myname.show_name()
	myname.show_facebook_page()
	myname.about()
	myname.show_art()
		