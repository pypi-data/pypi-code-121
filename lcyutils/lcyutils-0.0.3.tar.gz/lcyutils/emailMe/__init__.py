# %%
import smtplib
from email.mime.text import MIMEText
from email.header import Header

mail_user = "luochengyu1317@163.com"  

def dectry(p,key):
    k = key*10
    dec_str = ""
    for i,j in zip(p.split("_")[:-1],k):
        # i 为加密字符，j为秘钥字符
        temp = chr(int(i) - ord(j)) # 解密字符 = (加密Unicode码字符 - 秘钥字符的Unicode码)的单字节字符
        dec_str = dec_str+temp
    return dec_str

def lcy_email(to_list, key, mailSender = "落城雨",sub = "Auto Mail", content = "Lcy Tools - Auto Mail"):
    me = mailSender +"<"+mail_user+">"
    msg = MIMEText(content, _subtype='plain', _charset='utf-8')
    msg['Subject'] = sub    
    msg['From'] = me
    msg['To'] = ";".join(to_list)

    try:
        server = smtplib.SMTP()
        server.connect("smtp.163.com")
        server.login(mail_user, dectry("187_195_170_172_206_189_181_191_190_182_186_185_181_211_188_196_",key))
        server.sendmail(me, to_list, msg.as_string())
        server.close()
        return "Send Mail Success"
    except:
        print("Mail Error")
        return "Send Mail Failed"

def lcy_email_help():
    print("lcy_email:\n" \
          "- to_list: 一个list代表想要发送的对象\n" \
          "- mailSender: 发送人\n" \
          "- topic: 主题\n" \
          "- content: 内容\n" \
          "TODO: 更新附件功能\n"
    )
# send_mail(mailto_list)