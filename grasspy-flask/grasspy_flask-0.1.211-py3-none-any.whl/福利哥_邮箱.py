from flask_mail import Mail, Message

类 〇邮箱(Mail):
    """管理电子邮箱的邮件发送
    """
    套路 初始化应用(分身, 应用):
        返回 分身.init_app(应用)

    套路 发送(分身, 邮件):
        分身.send(邮件)

类 〇邮件(Message):
    """电子邮件对象
    """
    套路 __init__(
        分身,
        主题='',
        收件人=空,
        正文=空,
        html=空,
        发送人=空,
        抄送=空,
        秘密抄送=空,
        附件=空,
        回复地址=空,
        日期=空,
        字符集=空,
        额外头信息=空,
        邮箱选项=空,
        接收选项=空,
    ):
        super().__init__(
            subject=主题,
            recipients=收件人,
            body=正文,
            html=html,
            sender=发送人,
            cc=抄送,
            bcc=秘密抄送,
            attachments=附件,
            reply_to=回复地址,
            date=日期,
            charset=字符集,
            extra_headers=额外头信息,
            mail_options=邮箱选项,
            rcpt_options=接收选项
        )