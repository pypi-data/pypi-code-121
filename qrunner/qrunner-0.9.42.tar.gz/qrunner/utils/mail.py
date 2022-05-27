import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header


# 邮件通知
from qrunner.utils.allure_data import AllureData
from qrunner.utils.config import conf


class Mail:
    def __init__(self, host, user, password):
        self.host = host
        self.username = user
        self.password = password

    def send_mail(self, mail_data, receivers):
        print(f'向{receivers}发送邮件...')
        # 创建一个带附件的实例
        message = MIMEMultipart()
        message['From'] = Header(self.username)
        message['To'] = Header(",".join(receivers))
        message['Subject'] = Header(mail_data.get('title'), 'utf-8')

        # 邮件正文内容
        message.attach(MIMEText(mail_data.get('body'), 'plain', 'utf-8'))
        # 附件
        file_path = mail_data.get('file_path')
        if file_path:
            # 构造附件，传送当前目录下的文件
            att1 = MIMEText(open(file_path, 'r').read(), 'base64', 'utf-8')
            att1["Content-Type"] = 'application/octet-stream'
            # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
            file_name = mail_data.get('file_name')
            att1["Content-Disposition"] = f'attachment; filename="{file_name}"'
            message.attach(att1)

        # 连接
        conn = smtplib.SMTP_SSL(self.host, 465)
        # 登录
        conn.login(self.username, self.password)
        # 发送邮件
        try:
            conn.sendmail(self.username, receivers, message.as_string())
        except Exception as e:
            print(f'发送失败: {str(e)}')
        else:
            print('发送成功')
        # 断开连接
        conn.quit()

    def send_report(self, title, report_url, receiver_list):
        report_path = conf.get_item('common', 'report_path')
        allure_data = AllureData(report_path).get_basic_info()
        total = allure_data.get('total')
        fail = allure_data.get('fail')
        passed = allure_data.get('passed')
        rate = allure_data.get('rate')

        # 邮件内容
        title = f'{title}({time.strftime("%m-%d %H:%M")})'
        body_str = '\n\n共 {0} 个用例，通过 {1} 个，失败 {2} 个，通过率 {3}%，详见: {4}'\
            .format(total, passed, fail, rate, report_url)
        msg_data = {
            'title': title,
            'body': body_str,
            'file_path': None,
            'file_name': None
        }

        # 发送邮件
        self.send_mail(msg_data, receiver_list)




