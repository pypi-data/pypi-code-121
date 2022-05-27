_A=None
import logging,re
from email.header import Header
from email.message import Message
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import Dict,List,Optional,Union
from localstack.utils.common import now_utc
from localstack.utils.testutil import is_local_test_mode
from localstack_ext import config
from localstack_ext.bootstrap import smtplib_patched
LOG=logging.getLogger(__name__)
SENT_EMAILS=[]
EMAIL_BLACKLIST=set()
def is_smtp_configured():return config.SMTP_HOST
def get_canonical_email(email):A=email;A=re.sub('\\s+','',str(A or''));A=A.strip().lower();return A
def connect_smtp(smtp_host,smtp_user,smtp_pass):
	D=smtp_pass;C=smtp_user;A=smtplib_patched.SMTP(smtp_host)
	try:A.starttls()
	except Exception as B:LOG.debug('Unable to run STARTTLS command on SMTP connection: %s'%B)
	if C and D:
		try:A.login(C,D)
		except Exception as B:LOG.debug('Unable to run login/auth command against SMTP server, skipping: %s'%B)
	return A
def send_email(subject,text_message,recipients,from_email=_A,from_name=_A,smtp_host=_A,smtp_user=_A,smtp_pass=_A,images=_A,html_message=_A):
	J=text_message;I=subject;G=smtp_pass;F=smtp_user;E=from_name;C=smtp_host;B=from_email;A=recipients;C=C or config.SMTP_HOST;F=F or config.SMTP_USER;G=G or config.SMTP_PASS;B=B or config.SMTP_EMAIL;E=E or'LocalStack'
	if not C:
		if is_local_test_mode():L={'time':now_utc(),'smtp_host':C,'smtp_user':F,'smtp_pass':G,'from_email':B,'from_name':E,'subject':I,'message':J,'recipients':A};SENT_EMAILS.append(L);return
		LOG.debug('SMTP settings not configured, skip sending email to "%s"'%A);return
	A=A if isinstance(A,list)else[A];H=construct_message(I,J,E,B,images=images,html_message=html_message);sign_message(H)
	for D in A:
		if D in EMAIL_BLACKLIST:LOG.debug('Skip sending email to receiver in blacklist: %s'%D);continue
		LOG.debug('Sending email to %s'%D);H['To']=D;K=connect_smtp(C,F,G);K.sendmail(B,D,H.as_string());K.quit()
def send_email_message(message):A=connect_smtp(config.SMTP_HOST,config.SMTP_USER,config.SMTP_PASS);A.send_message(message);A.quit()
def sign_message(msg):0
def is_email_address(value):return re.match('[^@]+@[^@]+\\.[^@]+',value or'')
def construct_message(subject,text_message,from_name,from_email,images=_A,html_message=_A):
	E=text_message;C=html_message;B=images
	if B is _A:B={}
	A=MIMEText(E)
	if B or C:
		A=MIMEMultipart('related');D=MIMEMultipart('alternative');A.attach(D);D.attach(MIMEText(E))
		if C:D.attach(MIMEText(C,'html'))
		for (G,H) in B.items():F=MIMEImage(H);F.add_header('Content-ID','<%s>'%G);A.attach(F)
	A['Subject']=subject;A['From']=formataddr((str(Header(from_name,'utf-8')),from_email));return A