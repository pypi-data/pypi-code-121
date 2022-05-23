from ...utils.api import route, Parameter
from .. import mails

from alphaz.models.api import AlphaRequest

from core import core

api         = core.api
db          = core.db
log         = core.get_logger('api')

@route('/mails/mailme',logged=False,cache=False)
def mail_me():
    mails.mail_me(api,db)

@route('/mails/stayintouch',logged=False,cache=False, 
    parameters = [
        Parameter('token',required=True),
        Parameter('mail',required=True),
        Parameter('name',required=True)
    ])
def mails_stay_in_touch():
    token           = api.get('token')
    user_mail       = api.get('mail')
    name            = api.get('name')

    mails.stay_in_touch(api,user_mail,name, token,db)

@route('/mails/newsletter',
    parameters = [
        Parameter('mail',required=True),
        Parameter('name',required=True)
    ]
)
def mail_newsletter():
    db.add(defs.NewsLetter,values=api.get_parameters())
    return 'saved' 

@route('/mails/requestview',logged=False,cache=False, 
    parameters = [
        Parameter('token',required=True),
        Parameter('mail',required=True),
        Parameter('name',required=True),
        Parameter('id',required=True)
    ])
def mails_request_view():
    token       = api.get('token')
    user_mail   = api.get('mail')
    mail_type   = api.get('name')
    mail_id     = api.get('id')

    mails.request_view(api,user_mail,token,mail_type,mail_id,db)

@route('/mails/unsubscribe',logged=False,cache=False, 
    parameters = [
        Parameter('token',required=True),
        Parameter('mail',required=True),
        Parameter('type',required=True)
    ])
def mails_unsubscribe():
    token       = api.get('token')
    user_mail   = api.get('mail')
    mail_type   = api.get('type')

    mails.request_unsubscribe(api,user_mail,token,mail_type,db)