import os
from configparser import ConfigParser
from datetime import datetime

import boto3
import requests
from telegram import CallbackQuery

from digitalguide.whatsapp.WhatsAppUpdate import WhatsAppUpdate

config = ConfigParser()
config.read("config.ini")

if "space" in config.keys():
    session = boto3.session.Session()
    s3_client = session.client('s3',
                            region_name=config["space"]["region_name"],
                            endpoint_url=config["space"]["endpoint_url"],
                            aws_access_key_id=os.getenv('SPACES_KEY'),
                            aws_secret_access_key=os.getenv('SPACES_SECRET'))


def telegram_write_photo(update, context, bucket, folder):
    user_id = update.effective_user.id
    name = update.effective_user.name

    s3_client.put_object(Bucket=bucket,
                      Key=folder + "/" +
                      str(datetime.now())+"_" +
                      str(user_id) + '.jpg',
                      Body=update.message.photo[-1].get_file(
                      ).download_as_bytearray(),
                      ACL='private',
                      # Metadata={
                      #    'x-amz-meta-my-key': 'your-value'
                      # }
                      )


def whatsapp_write_photo(client, update: WhatsAppUpdate, context, bucket, folder):
    user_id = update.WaId
    name = update.ProfileName
    update.MediaUrl0

    s3_client.put_object(Bucket=bucket,
                      Key=folder + "/" +
                      str(datetime.now())+"_" +
                      str(user_id) + '.jpg',
                      Body=requests.get(update.MediaUrl0,
                                        allow_redirects=True).content,
                      ACL='private',
                      # Metadata={
                      #    'x-amz-meta-my-key': 'your-value'
                      # }
                      )


def telegram_write_message(update, context, bucket, folder):
    user_id = update.effective_user.id
    name = update.effective_user.name
    message = update.effective_message.text

    s3_client.put_object(Bucket=bucket,
                      Key=folder + "/" +
                      str(datetime.now())+"_" +
                      str(user_id) + '.txt',
                      Body=message,
                      ACL='private',
                      # Metadata={
                      #    'x-amz-meta-my-key': 'your-value'
                      # }
                      )


def whatsapp_write_message(client, update: WhatsAppUpdate, context, bucket, folder):
    user_id = update.WaId
    name = update.ProfileName
    message = update.Body

    s3_client.put_object(Bucket=bucket,
                      Key=folder + "/" +
                      str(datetime.now())+"_"+str(user_id) + '.txt',
                      Body=message,
                      ACL='private',
                      # Metadata={
                      #    'x-amz-meta-my-key': 'your-value'
                      # }
                      )


def telegram_write_voice(update, context, bucket, folder):
    user_id = update.effective_user.id
    name = update.effective_user.name

    s3_client.put_object(Bucket=bucket,
                      Key=folder + "/" +
                      str(datetime.now())+"_" +
                      str(user_id) + '.mp3',
                      Body=update.message.voice.get_file().download_as_bytearray(),
                      ACL='private',
                      # Metadata={
                      #    'x-amz-meta-my-key': 'your-value'
                      # }
                      )


def whatsapp_write_voice(client, update: WhatsAppUpdate, context, bucket, folder):
    user_id = update.WaId
    name = update.ProfileName

    s3_client.put_object(Bucket=bucket,
                      Key=folder + "/" +
                      str(datetime.now())+"_"+str(user_id) + '.mp3',
                      Body=requests.get(update.MediaUrl0,
                                        allow_redirects=True).content,
                      ACL='private',
                      # Metadata={
                      #    'x-amz-meta-my-key': 'your-value'
                      # }
                      )


def telegram_write(update, context, bucket, folder):
    if type(update) == CallbackQuery:
        pass
    elif update.message.voice:
        telegram_write_voice(update, context, bucket, folder)
    elif update.message.text:
        telegram_write_message(update, context, bucket, folder)
    elif update.message.photo:
        telegram_write_photo(update, context, bucket, folder)
    else:
        raise NotImplementedError("This type of update can not be saved")


def whatsapp_write(client, update: WhatsAppUpdate, context, bucket, folder):
    if update.MediaContentType0 and update.MediaContentType0.startswith("audio"):
        whatsapp_write_voice(client, update, context, bucket, folder)
    elif update.MediaContentType0 and update.MediaContentType0.startswith("image"):
        whatsapp_write_photo(client, update, context, bucket, folder)
    elif update.Body != "":
        whatsapp_write_message(client, update, context, bucket, folder)
    else:
        raise NotImplementedError("This type of update can not be saved")


telegram_action_functions = {"write_photo": telegram_write_photo,
                             "write_message": telegram_write_message,
                             "write_voice": telegram_write_voice,
                             "write": telegram_write
                             }

whatsapp_action_functions = {"write_photo": whatsapp_write_photo,
                             "write_message": whatsapp_write_message,
                             "write_voice": whatsapp_write_voice,
                             "write": whatsapp_write
                             }
