
import json
import random
import re
import time
from bs4 import BeautifulSoup
import requests
header = {
		'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
		'Accept': 'application/json, text/javascript, */*; q=0.01',
		'Accept-Language': 'en-US;q=0.7,en;q=0.3',
		'X-Requested-With': 'XMLHttpRequest',
		'Connection': 'keep-alive',
		'Referer': 'https://www.minuteinbox.com/',
	}
def parse_html(input):
    return(' '.join(BeautifulSoup(input, 'html.parser').stripped_strings))
New_Email_url="https://www.minuteinbox.com/index/new-email/"
index_url='https://www.minuteinbox.com/index/index'
refresh_url='https://www.minuteinbox.com/index/refresh'
get_inbox_url='https://www.minuteinbox.com/email/id/2'
delete_url='https://www.minuteinbox.com/delete'
domian="@ironflys.com"
def create_email(email):
	session = requests.session()
	data={"emailInput":email}
	
	r=session.post(New_Email_url,data=data,headers=header)
	print(r,r.text)
	
	minuteinbox_cookies=r.cookies
	if r.status_code==200:
		email=email+domian
		print("email is created")
		return email,session,minuteinbox_cookies,True
	else:
		return email,session,minuteinbox_cookies,False
def verify_email_isCreated(email,session,cookies):
	r = session.get(index_url, headers=header,cookies=cookies)
	r_email=json.loads(r.content.decode('utf-8-sig'))['email']
	email=email+domian
	print(email,r_email)
	if email!=r_email:
		return False
	else:
		return True
	
def get_inbox(session,cookies):
	
	r = session.get(refresh_url, headers=header, cookies=cookies)
	try:
		email_status=json.loads(parse_html(r.content.decode('utf-8-sig')))[0] #might bug here if there's weird special characters
		
	except Exception as e:
		print('\nERROR: Empty response from MinuteInbox, most likely caused by a bad character in the E-Mail\n')
		print(e)
		exit()
	
	if email_status['id'] == 2:
		raw_body=session.get(get_inbox_url, headers=header, cookies=cookies).text
		data={'subject': email_status['predmet'], 'sender': email_status['od'], 'raw_body': raw_body, 'clean_body': parse_html(raw_body)}
		return data
def delete_mail(session,cookies,email):
	r=session.get(delete_url,headers=header,cookies=cookies)
	if r.status_code==200:
		return True
	else:
		return False




	

