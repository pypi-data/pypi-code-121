class minesweeper:
	"""
	คลาส minesweeper คือ
	ข้อมูลที่เกี่ยวข้องกับ เรา
	ประกอบด้วยชื่อเพจ

	Example
	#-----------------------
	mine = minesweeper()
	mine.show_name()
	mine.show_page()
	mine.show_youtube()
	mine.about()
	mine.show_art()
	#-----------------------
	"""
	def __init__(self):
		self.name = 'Mine Sweeper'
		self.page = 'https://facebook.com/MineSweeper'

	def show_name(self):
		print('สวัสดีฉันชื่อ {}'.format(self.name))

	def show_page(self):
		print('FB page: {}'.format(self.page))

	def show_youtube(self):
		print('https://www.youtube.com/watch?v=cB2aVxYiXNQ')

	def about(self):
		text = """
		--------------------
		สวัสดีจ้า....ฉันคือชายโสด
		--------------------"""
		print(text)

	def show_art(self):
		text = """
		                    *

		             *  _|_
		             .-' * '-. *
		            /       * \
		         *  ^^^^^|^^^^^
		             .~. |  .~.
		            / ^ \\| / ^ \\
		           (|   |J/|   |)
		           '\\   /`"\\   /`
		 -- '' -'-'  ^`^    ^`^  -- '' -'-'

		"""
		print(text)



if __name__ == '__main__':
	mine = minesweeper()
	mine.show_name()
	mine.show_page()
	mine.show_youtube()
	mine.about()
	mine.show_art()

