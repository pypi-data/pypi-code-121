import logging
import re
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
def is_smtp_configured():
 return config.SMTP_HOST
def get_canonical_email(email):
 email=re.sub(r"\s+","",str(email or ""))
 email=email.strip().lower()
 return email
def connect_smtp(smtp_host:str,smtp_user:str,smtp_pass:str)->smtplib_patched.SMTP:
 s=smtplib_patched.SMTP(smtp_host)
 try:
  s.starttls()
 except Exception as e:
  LOG.debug("Unable to run STARTTLS command on SMTP connection: %s"%e)
 if smtp_user and smtp_pass:
  try:
   s.login(smtp_user,smtp_pass)
  except Exception as e:
   LOG.debug("Unable to run login/auth command against SMTP server, skipping: %s"%e)
 return s
def send_email(subject:str,text_message:str,recipients:Union[List,str],from_email:str=None,from_name=None,smtp_host=None,smtp_user=None,smtp_pass=None,images:Dict[str,bytes]=None,html_message:str=None):
 smtp_host=smtp_host or config.SMTP_HOST
 smtp_user=smtp_user or config.SMTP_USER
 smtp_pass=smtp_pass or config.SMTP_PASS
 from_email=from_email or config.SMTP_EMAIL
 from_name=from_name or "LocalStack"
 if not smtp_host:
  if is_local_test_mode():
   entry={"time":now_utc(),"smtp_host":smtp_host,"smtp_user":smtp_user,"smtp_pass":smtp_pass,"from_email":from_email,"from_name":from_name,"subject":subject,"message":text_message,"recipients":recipients}
   SENT_EMAILS.append(entry)
   return
  LOG.debug('SMTP settings not configured, skip sending email to "%s"'%recipients)
  return
 recipients=recipients if isinstance(recipients,list)else[recipients]
 message=construct_message(subject,text_message,from_name,from_email,images=images,html_message=html_message)
 sign_message(message)
 for recipient in recipients:
  if recipient in EMAIL_BLACKLIST:
   LOG.debug("Skip sending email to receiver in blacklist: %s"%recipient)
   continue
  LOG.debug("Sending email to %s"%recipient)
  message["To"]=recipient
  s=connect_smtp(smtp_host,smtp_user,smtp_pass)
  s.sendmail(from_email,recipient,message.as_string())
  s.quit()
def send_email_message(message:Message):
 s=connect_smtp(config.SMTP_HOST,config.SMTP_USER,config.SMTP_PASS)
 s.send_message(message)
 s.quit()
def sign_message(msg):
 pass
def is_email_address(value):
 return re.match(r"[^@]+@[^@]+\.[^@]+",value or "")
def construct_message(subject:str,text_message:str,from_name:str,from_email:str,images:Optional[Dict[str,bytes]]=None,html_message:Optional[str]=None)->MIMEBase:
 if images is None:
  images={}
 result=MIMEText(text_message)
 if images or html_message:
  result=MIMEMultipart("related")
  msg_alternative=MIMEMultipart("alternative")
  result.attach(msg_alternative)
  msg_alternative.attach(MIMEText(text_message))
  if html_message:
   msg_alternative.attach(MIMEText(html_message,"html"))
  for image_id,image_bytes in images.items():
   msg_image=MIMEImage(image_bytes)
   msg_image.add_header("Content-ID","<%s>"%image_id)
   result.attach(msg_image)
 result["Subject"]=subject
 result["From"]=formataddr((str(Header(from_name,"utf-8")),from_email))
 return result
# Created by pyminifier (https://github.com/liftoff/pyminifier)
