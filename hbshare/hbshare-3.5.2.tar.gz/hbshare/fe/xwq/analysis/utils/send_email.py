# -*- coding: utf-8 -*-

from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import  MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from os.path import basename
import os
import pandas as pd
import smtplib
import sys
import traceback
import zipfile


def zip_directory_file(path_name, file_name):
    zip_file = zipfile.ZipFile(file_name, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(path_name):
        for file in files:
            zip_file.write(os.path.join(root, file), file, zipfile.ZIP_DEFLATED)
    zip_file.close()
    return


def convert_df_to_html(df, title):
    taitou = [''] + list(df.columns)
    value = list(df.reset_index().values)
    # with open('table.html', 'w') as file: # 以w的模式打开file.html文件，不存在就新建
    table_str = ''
    taitou_str = ''
    for i in taitou:
        taitou_str = taitou_str + '<th>{}</th>'.format(i)
    table_str = '<table border=1><tr>{}</tr><indent>{}'.format(taitou_str, title)
    for i in range(df.shape[0]):
        i_str = ''
        for j in value[i]:
            i_str = i_str + '<td>{}</td>'.format(j)
        table_str += '<tr>{}</tr>'.format(i_str)
    table_str += '</indent></table>'
    return table_str


class SendEmail:
    @staticmethod
    def send_email(receiver, title, content, file_names=[], html=False, sender=None):
        send_success = False
        receivers = receiver.split(',')
        # 三个参数，第一个为文本内容，第二个 plain 设置文本格式， 第三个 utf-8 设置编码
        message = MIMEMultipart()
        message['From'] = Header(sender)
        message['To'] = Header(receiver)
        message['Subject'] = Header(title)
        message.attach(MIMEText(content, 'plain' if not html else 'html', _charset='utf-8'))
        try:
            for f in file_names or []:
                zf = open(f, 'rb')
                part = MIMEBase('application', 'zip')
                part.set_payload(zf.read())
                encoders.encode_base64(part)
                zf.close()
                part.add_header('Content-Disposition', 'attachment', filename=basename(f))
                message.attach(part)
            smtpObj = smtplib.SMTP('smtp.mxhichina.com', 25)
            smtpObj.set_debuglevel(0)
            smtpObj.login(sender, 'Xwq0930305$2')
            smtpObj.sendmail(sender, receivers, message.as_string())
            print("[SendEmail] send email success.")
            send_success = True
        except smtplib.SMTPException:
            exc_type, exc_value, exc_trackback = sys.exc_info()
            print(repr(traceback.format_exception(exc_type, exc_value, exc_trackback)))
            print("[SendEmail] send email error.")
            send_success = False
        return send_success