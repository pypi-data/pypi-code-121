import os
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from licsber.github import get_secret
from licsber.utils.utime import localtime_date_str


def _parse_dict(detail: dict) -> str:
    res = ''
    for i in detail:
        res += str(i) + ': ' + str(detail[i]) + '<br>'
    return res


class SMTP:
    def __init__(self, password=get_secret('L_SMTP_PWD'),
                 mail_address=get_secret('L_SMTP_ADDRESS'),
                 smtp_server=get_secret('L_SMTP_SERVER', 'smtp.qq.com'),
                 sender=None,
                 username=None):
        if not sender:
            sender = mail_address

        if not username:
            username = mail_address

        self.sender = sender
        self.smtp = smtplib.SMTP()

        self.smtp.connect(smtp_server)
        self.smtp.login(username, password)

    def plain_mail_to(self, title: str, body: str,
                      receiver=None,
                      mail_from='Licsber Automatic'):
        if not receiver:
            receiver = self.sender

        msg = MIMEText(body, 'plain', 'utf-8')
        msg["Accept-Language"] = "zh-CN"
        msg["Accept-Charset"] = "ISO-8859-1,utf-8"
        msg['Sender'] = mail_from
        msg['From'] = self.sender
        msg['To'] = receiver
        msg['Subject'] = Header(title, 'utf-8')

        try:
            self.smtp.sendmail(self.sender, receiver, msg.as_string())
            return True
        except smtplib.SMTPException:
            return False

    def notice_mail_to(self, mail_title: str, content_title: str, detail: any,
                       receiver=None,
                       mail_from='Licsber Automatic'):
        """
        发送提醒邮件.
        :param mail_title: 邮件标题 第一时间收到的.
        :param content_title: 在最中间的最大标题.
        :param detail: 推荐传递各种状态.
        :param receiver: 收件人 默认为提醒自己.
        :param mail_from: 发件人
        :return:
        """
        if not receiver:
            receiver = self.sender

        if type(detail) is dict:
            detail = _parse_dict(detail)

        mail_title = localtime_date_str() + ' ' + mail_title

        msg = MIMEMultipart('alternative')

        msg["Accept-Language"] = "zh-CN"
        msg["Accept-Charset"] = "ISO-8859-1,utf-8"
        msg['Sender'] = mail_from
        msg['From'] = self.sender
        msg['To'] = receiver
        msg['Subject'] = Header(mail_title, 'utf-8')
        template_path = os.path.join(os.path.dirname(__file__), 'notice_template.html')
        html = open(template_path).read()
        html = html.replace('{{title}}', content_title)
        html = html.replace('{{detail}}', detail)

        html = MIMEText(html, 'html')
        msg.attach(html)

        try:
            self.smtp.sendmail(self.sender, receiver, msg.as_string())
            return True
        except smtplib.SMTPException:
            return False
