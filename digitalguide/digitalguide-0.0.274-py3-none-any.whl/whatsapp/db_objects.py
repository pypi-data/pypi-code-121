import mongoengine
from telegram.constants import MAX_MESSAGE_LENGTH
import datetime

from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

dbname = config["bot"]["bot_name"]
class WhatsappUser(mongoengine.Document):
    ProfileName = mongoengine.StringField(required=True)
    WaId = mongoengine.StringField(required=True, max_length=50)
    entry_time = mongoengine.DateTimeField(default=datetime.datetime.utcnow)
    meta = {'db_alias': dbname}

class WhatsappInteraction(mongoengine.Document):
    user = mongoengine.ReferenceField(WhatsappUser)
    Latitude = mongoengine.StringField()
    Longitude = mongoengine.StringField()
    SmsMessageSid = mongoengine.StringField()
    NumMedia = mongoengine.StringField()
    ProfileName = mongoengine.StringField()
    SmsSid = mongoengine.StringField()
    WaId = mongoengine.StringField()
    SmsStatus = mongoengine.StringField()
    Body = mongoengine.StringField()
    To = mongoengine.StringField()
    NumSegments = mongoengine.StringField()
    MessageSid = mongoengine.StringField()
    AccountSid = mongoengine.StringField()
    From = mongoengine.StringField()
    ApiVersion = mongoengine.StringField()
    MediaContentType0 = mongoengine.StringField()
    MediaUrl0 = mongoengine.StringField()
    MessagingServiceSid = mongoengine.StringField()
    ReferralNumMedia = mongoengine.StringField()
    date = mongoengine.DateTimeField(default=datetime.datetime.utcnow)
    meta = {'db_alias': dbname}

class WhatsappUserContextState(mongoengine.Document):
    WaId = mongoengine.StringField()
    context = mongoengine.DictField()
    state = mongoengine.StringField()
    meta = {'db_alias': dbname}