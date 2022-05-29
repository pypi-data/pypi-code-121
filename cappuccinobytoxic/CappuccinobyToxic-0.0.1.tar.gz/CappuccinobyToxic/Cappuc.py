class Cappuccino:
	"""
	class Cappuccino คือ
	วิธีทำกาแฟ Capupuccino
	------------------------
	myname = Cappuccino()
	myname.show_name()
	myname.about()
	------------------------
	"""

	def __init__(self):
		self.name = 'Toxicboy'
		self.music = 'https://www.youtube.com/watch?v=2Omj-JHAI7A'
	
	def show_name(self):
		print(f'hello i am {self.name}')

	def show_how_to(self):
		text = '''
		1.First, steam the milk. Heat 1 cup of milk in a 2-quart saucepan over medium heat.
		2.Next, whip the milk with an electric mixer, increasing the speed as the milk begins to thicken. Continue mixing until you get the desired volume of froth.
		3.Now, make the coffee.
		4.Now, make the cappuccino!

		'''
		print(text)
	def show_wedsite(self,eng = False,open=False):
		if	eng == True:
			url = 'https://www.folgerscoffee.com/coffee/how-to/make-cappuccino'
			print(url)
			if open == True:
				webbrowser.open(url)
		else:
			pass   
if __name__=='__main__':
	myname = Cappuccino()
	myname.show_name()
	myname.show_how_to()
	myname.show_wedsite(True)