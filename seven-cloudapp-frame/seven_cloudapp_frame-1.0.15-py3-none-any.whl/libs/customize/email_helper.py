# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2022-03-03 11:04:55
@LastEditTime: 2022-03-03 11:49:20
@LastEditors: HuangJianYi
@Description: 
"""
from seven_framework import *
from seven_cloudapp_frame.models.seven_model import InvokeResultData
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr


class EmailHelper:
    """
    :description: 邮件帮助类
    """
    logger_error = Logger.get_logger_by_name("log_error")
    
    @classmethod
    def send(self, send_email, send_email_password, receive_emails, title, message, smtp_demain="smtp.qq.com", smtp_port=465):
        """
        :description:发送邮件
        :param send_email: 发件人邮箱账号
        :param send_email_password:发件人邮箱密码(当时申请smtp给的口令)
        :param receive_email:收件人邮箱账号
        :param title:标题
        :param content:内容
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            receive_email_list = []
            if receive_emails:
                receive_email_list = receive_emails.split(',')
            if len(receive_email_list) > 0:
                for receive_email in receive_email_list:
                    msg = MIMEText(message,'plain','utf-8')
                    msg['From'] = formataddr([send_email, send_email])
                    msg['To'] = formataddr([receive_email, receive_email])
                    msg['Subject'] = title

                    server = smtplib.SMTP_SSL(smtp_demain, smtp_port)  # 发件人邮箱中的SMTP服务器，端口是465
                    server.login(send_email, send_email_password)  # 括号中对应的是发件人邮箱账号、邮箱密码
                    server.sendmail(send_email, [
                        receive_email,
                    ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
                    server.quit()# 关闭连接
        except:
            self.logger_error.error("【send_email】" + traceback.format_exc())
            invoke_result_data.success = False
            invoke_result_data.error_code = "exception"
            invoke_result_data.error_message = traceback.format_exc()
            return invoke_result_data
        return invoke_result_data
