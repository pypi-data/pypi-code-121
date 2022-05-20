import logging
from telegram.ext import BasePersistence
from collections import defaultdict
from copy import deepcopy
from telegram.utils.helpers import decode_user_chat_data_from_json, decode_conversations_from_json, encode_conversations_to_json
import mongoengine
import json
from bson import json_util
import os

class Conversations(mongoengine.Document):
    obj = mongoengine.DictField()
    meta = { 'collection': 'Conversations', 'ordering': ['-id']}

class UserData(mongoengine.Document):
    obj = mongoengine.DictField()
    meta = { 'collection': 'UserData', 'ordering': ['-id']}

class ChatData(mongoengine.Document):
    obj = mongoengine.DictField()
    meta = { 'collection': 'ChatData', 'ordering': ['-id']}

class BotData(mongoengine.Document):
    obj = mongoengine.DictField()
    meta = { 'collection': 'BotData', 'ordering': ['-id']}

from pymongo import monitoring

logger = logging.getLogger(__name__)

class CommandLogger(monitoring.CommandListener):

    def started(self, event):
        logger.debug("Command {0.command_name} with request id "
                 "{0.request_id} started on server "
                 "{0.connection_id}".format(event))

    def succeeded(self, event):
        logger.debug("Command {0.command_name} with request id "
                 "{0.request_id} on server {0.connection_id} "
                 "succeeded in {0.duration_micros} "
                 "microseconds".format(event))

    def failed(self, event):
        logger.debug("Command {0.command_name} with request id "
                 "{0.request_id} on server {0.connection_id} "
                 "failed in {0.duration_micros} "
                 "microseconds".format(event))

monitoring.register(CommandLogger())

class DBHelper():
    """Class to add and get documents from a mongo database using mongoengine
    """
    def __init__(self, dbname):
        with open("ca-certificate.crt", "w") as text_file:
            text_file.write(os.getenv('DATABASE_CERT'))
        mongoengine.connect(host="mongodb+srv://"+ os.getenv("DATABASE_USERNAME")+":"+ os.getenv("DATABASE_PASSWORD") + "@" +os.getenv("DATABASE_HOST") +"/"+dbname+"?authSource=admin&tls=true&tlsCAFile=ca-certificate.crt")
    
    def add_item(self, data, collection):
        if collection == "Conversations":
            document = Conversations(obj=data)
        elif collection == "UserData":
            document = UserData(obj=data)
        elif collection == "ChatData":
            document = ChatData(obj=data)
        else:
            document = BotData(obj=data)
        document.save()
    def get_item(self, collection):
        if collection == "Conversations":
            document = Conversations.objects()
        elif collection == "UserData":
            document = UserData.objects()
        elif collection == "ChatData":
            document = ChatData.objects()
        else:
            document = BotData.objects()
        if document.first() is None:
            document = {}
        else:
            document = document.first()['obj']

        return document
    def close(self):
        mongoengine.disconnect()

class DBPersistence(BasePersistence):
    """Uses DBHelper to make the bot persistant on a database.
       It's heavily inspired on PicklePersistence from python-telegram-bot
    """
    def __init__(self, dbname):
        super(DBPersistence, self).__init__(store_user_data=True,
                                               store_chat_data=True,
                                               store_bot_data=True)
        self.persistdb = dbname
        self.conversation_collection = "Conversations"
        self.user_data_collection = "UserData"
        self.chat_data_collection = "ChatData"
        self.bot_data_collection = "BotData"
        self.db = DBHelper(dbname=dbname)
        self.user_data = None
        self.chat_data = None
        self.bot_data = None
        self.conversations = None
        self.on_flush = False

    def get_conversations(self, name):
        if self.conversations:
            pass
        else:
            conversations_json = json_util.dumps(self.db.get_item(self.conversation_collection))
            self.conversations = decode_conversations_from_json(conversations_json)
        return self.conversations.get(name, {}).copy()

    def update_conversation(self, name, key, new_state):
        if self.conversations.setdefault(name, {}).get(key) == new_state:
            return
        self.conversations[name][key] = new_state
        if not self.on_flush:
            conversations_json = json_util.loads(encode_conversations_to_json(self.conversations))
            self.db.add_item(conversations_json, self.conversation_collection)

    def get_user_data(self):
        if self.user_data:
            pass
        else:
            user_data_json = json_util.dumps(self.db.get_item(self.user_data_collection))
            if user_data_json != '{}':
                self.user_data = decode_user_chat_data_from_json(user_data_json)
            else:
                self.user_data = defaultdict(dict,{})
        return deepcopy(self.user_data)

    def update_user_data(self, user_id, data):
        if self.user_data is None:
            self.user_data = defaultdict(dict)
        # comment next line if you want to save to db every time this function is called
        if self.user_data.get(user_id) == data:
            return
        self.user_data[user_id] = data
        if not self.on_flush:
            user_data_json = json_util.loads(json.dumps(self.user_data))
            self.db.add_item(user_data_json, self.user_data_collection)

    def get_chat_data(self):
        if self.chat_data:
            pass
        else:
            chat_data_json = json_util.dumps(self.db.get_item(self.chat_data_collection))
            if chat_data_json != "{}":
                self.chat_data = decode_user_chat_data_from_json(chat_data_json)
            else:
                self.chat_data = defaultdict(dict,{})
        return deepcopy(self.chat_data)

    def update_chat_data(self, chat_id, data):
        if self.chat_data is None:
            self.chat_data = defaultdict(dict)
        # comment next line if you want to save to db every time this function is called
        if self.chat_data.get(chat_id) == data:
            return
        self.chat_data[chat_id] = data
        if not self.on_flush:
            chat_data_json = json_util.loads(json.dumps(self.chat_data))
            self.db.add_item(chat_data_json, self.chat_data_collection)

    def get_bot_data(self):
        if self.bot_data:
            pass
        else:
            bot_data_json = json_util.dumps(self.db.get_item(self.bot_data_collection))
            self.bot_data = json.loads(bot_data_json)
        return deepcopy(self.bot_data)

    def update_bot_data(self, data):
        if self.bot_data == data:
            return
        self.bot_data = data.copy()
        if not self.on_flush:
            bot_data_json = json_util.loads(json.dumps(self.bot_data))
            self.db.add_item(self.bot_data, self.bot_data_collection)

    def flush(self):
        if self.conversations:
            conversations_json = json_util.loads(encode_conversations_to_json(self.conversations))
            self.db.add_item(conversations_json, self.conversation_collection)
        if self.user_data:
            user_data_json = json_util.loads(json.dumps(self.user_data))
            self.db.add_item(user_data_json, self.user_data_collection)
        if self.chat_data:
            chat_data_json = json_util.loads(json.dumps(self.chat_data))
            self.db.add_item(chat_data_json, self.chat_data_collection)
        if self.bot_data:
            bot_data_json = json_util.loads(json.dumps(self.bot_data))
            self.db.add_item(self.bot_data, self.bot_data_collection)
        self.db.close()