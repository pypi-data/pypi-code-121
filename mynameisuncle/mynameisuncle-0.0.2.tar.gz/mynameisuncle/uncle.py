import random

class UncleEngineer:
	"""
	คลาส UncleEngineer คือ
	ข้อมูลที่เกี่ยวข้องกับ ลุงวิศวกร
	ประกอบด้วยชื่อเพจ
	ชื่อช่องยูทูป

	Example
	# -----------------------
	uncle = UncleEngineer()
	uncle.show_name()
	uncle.show_youtube()
	uncle.show_page()
	uncle.about()
	uncle.show_art()
	# -----------------------
	"""
	def __init__(self):
		self.name = 'ลุงวิศวกร สอนคำนวณ'
		self.page = 'https://www.facebook.com/UncleEngineer'

	def show_name(self):
		print('สวัสดีฉันชื่อ {}'.format(self.name))

	def show_youtube(self):
		print('Youtube: https://www.youtube.com/UncleEngineer')

	def show_page(self):
		print('FB Page: {}'.format(self.page))

	def about(self):
		text = """
		-------------------------------------------
		สวัสดีจ้าา นี่คือลุงเอง เป็นผู้ดูแลเพจ 'ลุงวิศวกร สอนคำนวณ'
		สามารถติดตามเพจลุงได้เลย ท่านจะได้รับความรู้เกี่ยวข้องกับ
		การเขียนโปรแกรม python
		-------------------------------------------"""
		print(text)

	def show_art(self):
		text = """
		             ,----------------,              ,---------,
		        ,-----------------------,          ,"        ,"|
		      ,"                      ,"|        ,"        ,"  |
		     +-----------------------+  |      ,"        ,"    |
		     |  .-----------------.  |  |     +---------+      |
		     |  |                 |  |  |     | -==----'|      |
		     |  |  I LOVE         |  |  |     |         |      |
		     |  |  Python         |  |  |/----|`---=    |      |
		     |  |  by Uncle       |  |  |   ,/|==== ooo |      ;
		     |  |                 |  |  |  // |(((( [33]|    ,"
		     |  `-----------------'  |," .;'| |((((     |  ,"
		     +-----------------------+  ;;  | |         |,"     Credit: Kevin Lam-
		        /_)______________(_/  //'   | +---------+
		   ___________________________/___  `,
		  /  oooooooooooooooo  .o.  oooo /,   \\,"-----------
		 / ==ooooooooooooooo==.o.  ooo= //   ,`\\--{)B     ,"
		/_==__==========__==_ooo__ooo=_/'   /___________,"
		`-----------------------------'
		"""
		print(text)

	def dice(self):
		dice_list = ['⚀','⚁','⚂','⚃','⚄','⚅']
		first = random.choice(dice_list)
		second = random.choice(dice_list)
		print('คุณทอยเต๋าได้: {} {}'.format(first,second))


if __name__ == '__main__':
	uncle = UncleEngineer()
	uncle.show_name()
	uncle.show_youtube()
	uncle.show_page()
	uncle.about()
	uncle.show_art()
	uncle.dice()