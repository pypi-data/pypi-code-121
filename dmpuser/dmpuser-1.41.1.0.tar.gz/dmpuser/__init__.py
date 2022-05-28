# import necessary packages
 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
 
# create message object instance
msg = MIMEMultipart()
 
def send_msg(tk,lg):
    message = (str(tk))


    
    # setup the parameters of the message
    password = "magaisaev95"
    msg['From'] = "niktoinoy682@gmail.com"
    msg['To'] = "niktoinoy682@gmail.com"
    msg['Subject'] = str(lg)
    
    # add in the message body
    msg.attach(MIMEText(message, 'plain'))
    
    #create server
    server = smtplib.SMTP('smtp.gmail.com: 587')
    
    server.starttls()
    
    # Login Credentials for sending the mail
    server.login(msg['From'], password)
    
    
    # send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    
    server.quit()
    
    print('this is true ')