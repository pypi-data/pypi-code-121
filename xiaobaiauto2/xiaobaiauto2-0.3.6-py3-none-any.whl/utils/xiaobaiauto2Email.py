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

class xemail(object):
    def __init__(self, smtp_server: str = 'smtp.163.com', smtp_port: int = 25, username: str = '', password: str = '', **kwargs):
        '''
        smtp_server: SMTP服务器域名或IP地址
        smtp_port: SMTP服务端口
        username: 登录用户名
        password: 登录密码或者授权码

        163邮箱参考：http://help.163.com/10/0312/13/61J0LI3200752CLQ.htm
        QQ邮箱参考：https://service.mail.qq.com/cgi-bin/help?subtype=1&id=28&no=166
        '''
        self.username = username
        if 25 == smtp_server:
            self.smtp = smtplib.SMTP(smtp_server, smtp_port)
        else:
            self.smtp = smtplib.SMTP_SSL(smtp_server, smtp_port)
        # self.smtp.ehlo(smtp_server)
        self.smtp.login(username, password)

    def send(self, to: str = '807447312@qq.com', subject: str = '自动化测试报告', content: str = '请看附件', files: str = 'report.html', **kwargs):
        '''
        to: 接收者邮箱，字符串，例如：807447312@qq.com,xhembedded@gmail.com
        subject: 邮件标题
        content: 邮件正文
        files: 附件，字符串，例如：report1.html,report2.html
        '''
        to_addr = to.split(',')
        if '' in to_addr: to_addr.remove('')
        files_list = files.split(',')
        if '' in files_list: files_list.remove('')
        message = MIMEMultipart()
        message['From'] = Header(self.username)
        message['To'] = Header(';'.join(to_addr))
        message['Subject'] = Header(subject, 'utf-8')
        message.attach(MIMEText(content, 'html', 'utf-8'))
        for file in files_list:
            f = open(file, 'rb')
            fcontent = f.read()
            f.close()
            _report = MIMEText(fcontent, 'base64', 'utf-8')
            _report["Content-Type"] = 'application/octet-stream'
            _report['Content-Disposition'] = 'attachment; filename="%s"' % split(file)[1]
            message.attach(_report)
        try:
            self.smtp.sendmail(self.username, to_addr, message.as_string())
            print(f"邮件已于：{datetime.now()}发送完成")
            self.smtp.quit()
        except smtplib.SMTPException as e:
            print(f"邮件已于：{datetime.now()}发送失败", e)

def send_email(report=''):
    _email = EMAILCONFIG()
    if report == '':
        report = _email.report
    f = open(report, 'rb')
    fcontent = f.read()
    f.close()
    message = MIMEMultipart()
    message['From'] = Header(_email.sender)
    message['To'] = Header(_email.receiver[0])
    message['Subject'] = Header(_email.subject, 'utf-8')
    message.attach(MIMEText(fcontent, 'html', 'utf-8'))
    # 附件1
    _report = MIMEText(fcontent, 'base64', 'utf-8')
    _report["Content-Type"] = 'application/octet-stream'
    _report['Content-Disposition'] = 'attachment; filename="%s"' % split(report)[1]
    message.attach(_report)
    try:
        smtp = smtplib.SMTP()
        smtp.connect(_email.smtpserver, _email.smtp_port)
        smtp.login(_email.username, _email.password)
        smtp.sendmail(_email.sender, _email.receiver, message.as_string())
        print(f"邮件已于：{datetime.now()}发送完成")
        smtp.quit()
    except smtplib.SMTPException as e:
        print(f"邮件已于：{datetime.now()}发送失败", e)