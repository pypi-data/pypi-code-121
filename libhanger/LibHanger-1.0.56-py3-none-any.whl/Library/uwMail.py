import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate

class uwMail():
    
    """
    メール送受信クラス
    """
    
    def __init__(self, host, smtpPort, user, password):
        
        """
        コンストラクタ

        Parameters
        ----------
        host : str
            ホスト名
        smtpPort : str
            送信ポート番号
        user : str
            ユーザーアカウント
        password : str
            ユーザーパスワード
        """
        
        # stmpオブジェクト
        self.smtp = smtplib.SMTP(host, smtpPort)
        # メールサーバーに対する応答
        self.smtp.ehlo()
        # 暗号化通信開始
        self.smtp.starttls()
        self.smtp.ehlo()
        
        # ログイン
        self.smtp.login(user, password)

    def sendMail(self, mail_from, mail_to, subject, bodyText):

        """
        メール送信
        
        Parameters
        ----------
        mail_from : str
            送信元メールアドレス
        mail_from : str
            送信先メールアドレス
        subject : str
            件名
        bodyText : str
            メール本文
        """
                
        # メッセージオブジェクト
        msg = MIMEText(bodyText)
        msg['Subject'] = subject
        msg['From'] = mail_from
        msg['To'] = mail_to
        msg['Date'] = formatdate(localtime=True)
        
        # 送信
        self.smtp.sendmail(mail_from, mail_to, msg.as_string())