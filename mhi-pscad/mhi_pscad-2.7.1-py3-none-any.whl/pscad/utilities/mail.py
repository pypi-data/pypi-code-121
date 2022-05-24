# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Power Systems Computer Aided Design (PSCAD)
# ------------------------------------------------------------------------------
#  PSCAD is a powerful graphical user interface that integrates seamlessly
#  with EMTDC, a general purpose time domain program for simulating power
#  system transients and controls in power quality studies, power electronics
#  design, distributed generation, and transmission planning.
#
#  This Python script is a utiliy class.It has usefull functions that
#  can help you develop fully featured PSCAD scripts.
#
#     PSCAD Support Team <support@pscad.com>
#     Manitoba HVDC Research Centre Inc.
#     Winnipeg, Manitoba. CANADA
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


"""E-Mail Helper Utility"""

#---------------------------------------------------------------------
# Imports
#---------------------------------------------------------------------

import sys, smtplib, logging
from os.path import abspath, basename
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import win32com.client, pywintypes


#===============================================================================
# Logging
#===============================================================================

LOG = logging.getLogger(__name__)


#===========================================================================
# Mail Class
#---------------------------------------------------------------------------
# Provides the ability to send emails
#---------------------------------------------------------------------------

class Mail:

    """E-Mail Helper Utility"""

    #----------------------------------------------------------------------
    # send_gmail() - Sends an email using any gmail account
    #----------------------------------------------------------------------
    @staticmethod
    def send_gmail(sender: str, password: str,  # pylint: disable=too-many-arguments
                   recipients: list, subject: str, body: str,
                   attachments: list = None):

        """Sends a document using a GMail account"""

        # GMail requires recipients separated by commas
        if isinstance(recipients, str):
            recipients = recipients.replace(';', ',')
            recipients = recipients.split(",")

        # Create a list of attachments
        attachments = attachments or []
        if isinstance(attachments, str):
            attachments = [fn.strip() for fn in attachments.split(",")]
        attachments = [abspath(filename) for filename in attachments]

        # Create the enclosing (outer) message
        LOG.debug("Creating G-Mail email")

        mail = MIMEMultipart()
        mail.attach(MIMEText(body, 'plain'))
        mail['Subject'] = subject
        mail['To'] = ", ".join(recipients)
        mail['From'] = sender
        mail.preamble = 'You will not see this in a MIME-aware mail reader.\n'


        # Add the attachments to the message
        for file in attachments:
            try:
                LOG.debug("   Attaching %s", file)
                name = basename(file)
                with open(file, "rb") as fp:
                    mail.attach(MIMEApplication(
                        fp.read(),
                        Content_Disposition='attachment; filename="%s"' % name,
                        Name=name
                    ))
            except Exception:
                LOG.error("   Unable to open attachment %s", file)
                raise

        composed = mail.as_string()

        # Message is ready, send it!
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.ehlo()
            server.starttls()
            server.login(sender, password)

            server.sendmail(sender, recipients, composed)
            server.close()
            LOG.info("Successfully sent the G-Mail")

        except Exception as ex:
            LOG.error("Failed to send G-Mail: %s", ex)
            raise


    #----------------------------------------------------------------------
    # send_outlook_mail() - Sends an email using Microsoft Outlook
    #----------------------------------------------------------------------
    @staticmethod
    def send_outlook_mail(recipients: list, subject: str, body: str,
                          attachments: list = None):

        """Sends a document using a Microsoft Outlook account"""

        # Outlook requires recipients separated by semicolons
        if isinstance(recipients, str):
            recipients = recipients.replace(',', ';')
        else:
            recipients = ";".join(recipients)

        # Create a list of attachments
        attachments = attachments or []
        if isinstance(attachments, str):
            attachments = [fn.strip() for fn in attachments.split(",")]
        attachments = [abspath(filename) for filename in attachments]

        try:
            LOG.debug("Creating Microsoft Outlook email")
            ol_mail_item = 0x0
            obj = win32com.client.Dispatch("Outlook.Application")

            mail = obj.CreateItem(ol_mail_item)
            mail.Subject = subject
            mail.Body = body
            mail.To = recipients

            # Add the attachments to the message
            for file in attachments:
                LOG.debug("   Attaching %s", file)
                mail.Attachments.Add(file)

            mail.Send()
            LOG.info("Successfully sent the Outlook Email")

        except pywintypes.com_error as ex:
            LOG.error("Failed to send Outlook Email: %s", ex.args[2][2])
            raise


# Test Code, lets take this for a drive.
if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)

    SENDER = 'user_name_here@gmail.com'
    PASSWORD = 'password'
    TO = ['user@example.com', 'user2@example.com']
    SUBJECT = 'This email is being sent by a Python script'
    BODY = ('I am attaching files.\n'
            'Python is controlling Microsoft Outlook or '
            'GMail and is sending this email automatically !!!')
    ATTACHMENTS = [r'C:\Users\Public\Documents\mlp\test.txt',
                   r'C:\Users\Public\Documents\mlp\test.docx',
                   r'C:\Users\Public\Documents\mlp\test.jpg',
                   r'C:\Users\Public\Documents\mlp\test.xlsx']

    #Mail.send_gmail(SENDER, PASSWORD, TO, SUBJECT, BODY, ATTACHMENTS)
    #Mail.send_outlook_mail(TO, SUBJECT, BODY, ATTACHMENTS)

# ------------------------------------------------------------------------------
#  End of script
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
