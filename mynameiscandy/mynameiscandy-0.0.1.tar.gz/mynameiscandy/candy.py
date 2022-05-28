class Candylady:
	"""
	คลาส Candylady คือ
	ข้อมูลที่เกี่ยวข้องกับ คุณแคนดี้


	Example
	#---------------------
	candy = Candylady()
	candy.show_name()
	candy.show_youtube()
	candy.about()
	candy.show_art()
	#--------------------


	"""

	def __init__(self):
		self.name = 'Candy lady'
		self.page = 'https://www.youtube.com/watch?v=mKORVdoWU2E'

	def show_name(self):
		print('สวัสดีฉันชื่อ {}'.format(self.name))

	def show_youtube(self):
		print('https://www.youtube.com/watch?v=mKORVdoWU2E')

	def about(self):
		text = """
		สวัสดีจ้าา นี้คุณแคนดี้เองจ้า เป็นนักเรียนเพจลุงจ้า """
		print(text)

	def show_art(self):
		text = """
			                         .-.
		                        |/`\\.._
		     _..._,,--.         `\\ /.--.\\ _.-. 
		  ,/'  ..:::.. \\     .._.-'/    \\\\` .\\ 
		 /       ...:::.`\\ ,/:..| |(o)  / /o)|
		|:..   |  ..:::::'|:..  ;\\ `---'. `--'
		;::... |   .::::,/:..    .`--.   .:.`\\_
		 |::.. ;  ..::'/:..   .--'    ;\\   :::.`\
		 ;::../   ..::|::.  /'          ;.  ':'.---.
		  `--|    ..::;\\:.  `\\,,,____,,,/';\\. (_)  |)
		     ;     ..::/:\\:.`\\|         ,__,/`;----'
		     `\\       ;:.. \\: `-..      `-._,/,_,/
		       \\      ;:.   ). `\\ `>     _:\
		        `\\,  ;:..    \\ \\ _>     >'
		        """
		print(text)


if __name__ == '__main__':
	candy = Candylady()
	candy.show_name()
	candy.show_youtube()
	candy.about()
	candy.show_art()
