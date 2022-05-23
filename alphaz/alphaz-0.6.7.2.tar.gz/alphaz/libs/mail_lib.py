import smtplib, socks, copy, json

import hashlib, re, os, datetime
from flask import current_app
from flask_mail import Message

import uuid

from . import sql_lib
from ..models.config._utils import get_mails_parameters

REQUIRED_PARAMETERS         = ['mail']
KEY_SIGNATURE               = '<alpha mail>'
MAIL_PARAMETERS_PATTERN     = "[[%s]]"

def mail2(to_mails,subject,body,bodyHtml=None,attachments=[]):
    import win32com.client as win32
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.To = to_mails
    mail.Subject = subject
    mail.Body = body
    mail.HTMLBody = bodyHtml if bodyHtml is not None else body #this field is optional

    # To attach a file to the email (optional):
    if len(attachments) != 0:
    #attachment  = "Path to the attachment"
        for attachment in attachments:
            mail.Attachments.Add(attachment)

    mail.Send()

def mail(to_mails,from_mails,proxy_host, proxy_port):
    receivers = [to_mails]

    message = """From: From Person <from@fromdomain.com>
    To: To Person <to@todomain.com>
    Subject: SMTP e-mail test

    This is a test e-mail message.
    """
    
    if proxy_host is not None:
        socks.setdefaultproxy(socks.HTTP, proxy_host, proxy_port)
    socks.wrapmodule(smtplib)

    try:
       smtpObj = smtplib.SMTP('SMTP.office365.com')
       smtpObj.sendmail(from_mails, receivers, message)         
       print ("Successfully sent email")
    except Exception as ex:
       print ("Error: unable to send email: ",ex)
    
def get_mail_type(raw_mail_url):
    if 'mail-content=' in raw_mail_url:
        raw_mail_url = raw_mail_url.split('mail-content=')[1]
    if '&' in raw_mail_url:
        raw_mail_url = raw_mail_url.split('&')[0]
    return raw_mail_url

""" MAILS """
def get_mail_content(mail_root, mail_type,log):
    content = ""
    if not mail_root[-1] == os.sep:
        mail_root = mail_root + os.sep

    raw         = mail_type.split('?')[0]
    parameters  = {}
    if len(mail_type.split('?')) != 1:
        for el in mail_type.split('?')[1].split('&'):
            key, value = el.split('=')[0], el.split('=')[1]
            parameters[key] = value

    mail_path = mail_root + raw

    if os.path.exists(mail_path):
        with open(mail_path) as f:
            content  = f.read()

        for key, value in parameters.items():
            file_name  = mail_root + value + '.html'
            div_block  = r'<div id="%s">[^\<\>]*<\/div>'%key
            regex_find = re.findall(div_block,content)

            if len(regex_find) != 0:
                result = regex_find[0]
            else:
                log.error('Mail content is incorrect for %s, cannot div block by %s content (regex expression not matched: %s )'%(mail_path,file_name,div_block))
                return None

            with open(file_name) as f:
                div_content  = f.read()
            content = content.replace(result,div_content)
    else:
        log.error('Cannot find mail content at %s'%mail_path)
        return None

    script_starts = [m.start() for m in re.finditer('<script', content)]
    script_ends   = [m.start() for m in re.finditer('</script>', content)]

    script_blocks = []
    for i in range(len(script_starts)):
        script_blocks.append(content[script_starts[i]:script_ends[i] + len('</script>')])

    for script_block in script_blocks:
        content = content.replace(script_block,'')

    with open(mail_root + os.sep + 'generated_mail.html','w') as f:
        f.write(content)

    return content

def get_mail_token(key):
    salt        = "%ThisIsGolliath38Pepper$"
    hash_string = key + salt
    hashed      = hashlib.sha256(hash_string.encode()).hexdigest()
    return hashed

def is_mail_token_valid(key,token):
    hashed = get_mail_token(key)
    return hashed == token

def get_title(content,default=''):
    title_regex = r'<title[^>]*>([^<]+)</title>'
    regex_find = re.findall(title_regex,content)

    if len(regex_find) != 0:
        result = regex_find[0]
    else:
        result = default if default is not None else ''
    return result

def set_parameters(content,parameters):
    for parameter, value in parameters.items():
        if value is not None:
            content = content.replace(MAIL_PARAMETERS_PATTERN%parameter,str(value))
    return content

def add_mail_classic_parameter(parameters):
    now     = datetime.datetime.now()
    year    = now.year
    month   = now.month
    hour    = now.hour
    minute  = now.minute
    second  = now.second

    classic_parameters = {
        'year':year,
        'month':month,
        'hour':hour,
        'minute':minute,
        'second':second,
        'uuid': str(uuid.uuid4()),
        'mail_token': get_mail_token(parameters['mail'])
    }

    for key, value in classic_parameters.items():
        if not key in parameters:
            parameters[key] = value
    return parameters

def update_mail_content(content,mail_url,parameters,parameters_to_specify,log):
    parameters_to_keep          = {}
    for required_parameter in REQUIRED_PARAMETERS:
        if not required_parameter in parameters.keys():
            log.error('Missing parameter <%s> for sending mail !'%required_parameter)
            return content, False, parameters_to_keep

    parameters                  = add_mail_classic_parameter(parameters)
    parameters['configuration'] = get_mail_type(mail_url)

    raw_parameters = copy.copy(parameters)
    for key, value in raw_parameters.items():
        for k, v in parameters.items():
            if MAIL_PARAMETERS_PATTERN%key in str(v):
                parameters[k] = v.replace(MAIL_PARAMETERS_PATTERN%key,value)

    for key, value in parameters.items():
        if MAIL_PARAMETERS_PATTERN%key in parameters_to_specify:
            parameters_to_keep[key] = value

    content                     = set_parameters(content,parameters_to_keep)

    parameters_not_specified    = list(set(get_mails_parameters(content)))

    if len(parameters_not_specified) != 0:
        log.error('Missing parameters %s for mail "%s"'%(','.join(parameters_not_specified),mail_url))
        return content, False, parameters_to_keep

    """if not valid_signature:
        log.error('Invalid mail signature !')
        return False"""

    return content, True, parameters_to_keep

def get_mail_content_for_parameters(mail_path,mail_url,parameters_list,log):
    if not 'template' in mail_url:
        mail_url = 'template.html?mail-content=' + mail_url

    if log: 
        log.debug('Getting mail at %s/%s'%(mail_path,mail_url))

    content                 = get_mail_content(mail_path,mail_url,log)
    if content is None:
        return []
    parameters_to_specify   = get_mails_parameters(content)

    #valid_signature         = KEY_SIGNATURE in str(content) 

    mail_contents_list = []
    for parameters in parameters_list:        
        mail_contents_dict                      = {'content':None,'parameters':None,'valid':False}
        out_content, valid, pars                = update_mail_content(content,mail_url,parameters,parameters_to_specify,log)
        
        mail_contents_dict['content']           = out_content
        mail_contents_dict['parameters']        = pars
        mail_contents_dict['raw_parameters']    = parameters
        mail_contents_dict['valid']             = valid
        mail_contents_list.append(mail_contents_dict)
    return mail_contents_list

def send_mail(mail_path,mail_type,parameters_list,sender,db,log):
    mail_contents_list = get_mail_content_for_parameters(mail_path,mail_type,parameters_list,log)

    for config in mail_contents_list:        
        if is_mail_already_send(db,mail_type,config['parameters'],log=log):
            log.error('Mail already sent %s'%config)
            return False

        if is_blacklisted(db,config['raw_parameters']['mail'],mail_type):
            log.error('Mail adress <%s> blacklisted %s'%config['raw_parameters']['mail'])
            return False

        # Send mail
        msg     = Message(config['raw_parameters']['title'],
                    sender=sender,
                    recipients=[config['raw_parameters']['mail']])
        msg.html = config['content']
        current_app.extensions["mail"].send(msg)
        #api.mail.send(msg)

        # insert in history
        mail_type   = get_mail_type(mail_type)
        set_mail_history(db,mail_type,config['raw_parameters']['uuid'],config['parameters'],log=log)
        log.info('Sending mail to %s'%config['raw_parameters']['mail'])
    return True

def set_mail_history(db, mail_type,uuidValue,parameters,log=None):
    mail_type           = get_mail_type(mail_type)
    unique_parameters   = get_unique_parameters(parameters)
    query   = "INSERT INTO mail_history (uuid, mail_type, parameters, parameters_full) VALUES (%s,%s,%s,%s)"
    values  = (uuidValue,mail_type,json.dumps(unique_parameters),json.dumps(parameters))
    return db.execute_query(query,values)

def get_unique_parameters(parameter):
    unique_parameters = {}
    for key, value in parameter.items():
        if key[0:5] != 'page_': #TODO: check
            unique_parameters[key] = value
    return unique_parameters

def is_mail_already_send(db,mail_type,parameters,log=None):
    from ..models.database import main_definitions as defs
    mail_type           = get_mail_type(mail_type)
    unique_parameters   = get_unique_parameters(parameters)

    results             = db.select(defs.MailHistory,filters=[
        defs.MailHistory.mail_type==mail_type,
        defs.MailHistory.parameters==json.dumps(unique_parameters)
    ],json=True)
    return len(results) != 0

def is_blacklisted(db,user_mail,mail_type,log=None):
    from ..models.database import main_definitions as defs
    mail_type   = get_mail_type(mail_type)
    results             = db.select(defs.MailBlacklist,filters=[
        defs.MailBlacklist.mail_type==mail_type,
        defs.MailBlacklist.mail==user_mail
    ],json=True)
    return len(results) != 0



