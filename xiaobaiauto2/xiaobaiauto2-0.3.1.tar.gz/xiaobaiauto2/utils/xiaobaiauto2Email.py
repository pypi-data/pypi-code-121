#! /usr/bin/env python
__author__ = 'Tser'
__email__ = '807447312@qq.com'
__project__ = 'xiaobaiauto2'
__script__ = 'xiaobaiauto2Email.py'
__create_time__ = '2020/7/15 23:13'

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from xiaobaiauto2.config.config import EMAILCONFIG
from datetime import datetime
from os.path import split

def send_email(report=''):
    _emil = EMAILCONFIG()
    if report == '':
        report = _emil.report
    f = open(report, 'rb')
    fcontent = f.read()
    f.close()
    message = MIMEMultipart()
    message['From'] = Header(_emil.sender)
    message['To'] = Header(_emil.receiver[0])
    message['Subject'] = Header(_emil.subject, 'utf-8')
    message.attach(MIMEText(fcontent, 'html', 'utf-8'))
    # 附件1
    _report = MIMEText(fcontent, 'base64', 'utf-8')
    _report["Content-Type"] = 'application/octet-stream'
    _report['Content-Disposition'] = 'attachment; filename="%s"' % split(report)[1]
    message.attach(_report)
    try:
        smtp = smtplib.SMTP()
        smtp.connect(_emil.smtpserver, _emil.smtp_port)
        smtp.login(_emil.username, _emil.password)
        smtp.sendmail(_emil.sender, _emil.receiver, message.as_string())
        print(f"邮件已于：{datetime.now()}发送完成")
        smtp.quit()
    except smtplib.SMTPException as e:
        print(f"邮件已于：{datetime.now()}发送失败", e)