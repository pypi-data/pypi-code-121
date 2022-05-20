from PIL import Image
from io import BytesIO

from telegram import (Update)
from telegram.ext import (CallbackContext)

from digitalguide.whatsapp.WhatsAppUpdate import WhatsAppUpdate
from configparser import ConfigParser

config = ConfigParser()
config.read("config.ini")

def generate_gif(im1, im2):
    im1 = im1.resize((round(im2.size[0]*1), round(im2.size[1]*1)))
    im1 = im1.convert(im2.mode)

    images = []
    frames = 10

    for i in range(frames+1):
        im = Image.blend(im1, im2, i/frames)
        images.append(im)

    for i in range(frames+1):
        im = Image.blend(im1, im2, 1-i/frames)
        images.append(im)

    bio = BytesIO()
    bio.name = 'image.gif'

    images[0].save(bio, 'GIF', save_all=True,
                   append_images=images[1:], duration=150, loop=0, optimize=True)
    bio.seek(0)
    return bio


def overlay_images(background, foreground, x_position="left", y_position="up", resize=True):
    x_scale_ratio = foreground.size[0]/background.size[0]
    y_scale_ratio = foreground.size[1]/background.size[1]
    
    if x_scale_ratio >= y_scale_ratio:
        scale_ratio = foreground.size[0]/background.size[0]
        background = background.resize(
            (foreground.size[0], round(background.size[1]*scale_ratio)))
    elif x_scale_ratio < y_scale_ratio:
        scale_ratio = foreground.size[1]/background.size[1]
        background = background.resize(
            (round(background.size[0]*scale_ratio), foreground.size[1]))
    
    if x_position=="left":
        x_coordinate = 0
    elif x_position=="right":
        x_coordinate = background.size[0] - foreground.size[0]
    elif x_position=="middle":
        x_coordinate = background.size[0]/2 - foreground.size[0]/2

    if y_position =="up":
        y_coordinate = 0
    elif y_position =="middle":
        y_coordinate = background.size[1]/2 - foreground.size[1]/2
    elif y_position == "bottom":
        y_coordinate = background.size[1] - foreground.size[1]


    background.paste(foreground, (x_coordinate, y_coordinate), foreground)
    return background

def telegram_eval_image_overlay(update: Update, context: CallbackContext, picture, x_position="left", y_position="up", resize="x"):
    if resize in ["False", "false"]:
        resize = False

    im_bytes = update.message.photo[-1].get_file().download_as_bytearray()

    im_file = BytesIO(im_bytes)  # convert image to file-like object
    im1 = Image.open(im_file)   # img is now PIL Image object
    im2 = Image.open('assets/' + picture)

    new_im = overlay_images(im1, im2, x_position,y_position, resize)

    bio = BytesIO()
    bio.name = 'image.png'
    new_im.save(bio, 'PNG')
    bio.seek(0)

def whatsapp_eval_image_overlay(client, update, context, picture, x_position="left", y_position="up", resize="x"):
    import requests
    if resize in ["False", "false"]:
        resize = False

    im_bytes = requests.get(
            update.MediaUrl0, allow_redirects=True).content

    im_file = BytesIO(im_bytes)  # convert image to file-like object
    im1 = Image.open(im_file)   # img is now PIL Image object
    im2 = Image.open('assets/' + picture)

    new_im = overlay_images(im1, im2, x_position,y_position, resize)

    bio = BytesIO()
    bio.name = 'image.png'
    new_im.save(bio, 'PNG')
    bio.seek(0)

    import boto3
    import os
    import time
    session = boto3.session.Session()
    s3_client = session.client('s3',
                           region_name=config["space"]["region_name"],
                           endpoint_url=config["space"]["endpoint_url"],
                           aws_access_key_id=os.getenv('SPACES_KEY'),
                           aws_secret_access_key=os.getenv('SPACES_SECRET'))

    time_str = str(round(time.time() * 1000))

    s3_client.put_object(Bucket=config["space"]["bucket"],
                            Key= time_str  + "_" + str(update.WaId) + '.png',
                            Body=bio,
                            ACL='public-read',
                            ContentType='image/png'
                            # Metadata={
                            #    'x-amz-meta-my-key': 'your-value'
                            # }
                            )

    client.messages.create(
            media_url=config["space"]["url"] + "/" + time_str + "_" + str(update.WaId) + '.png',
            from_=update.To,
            to=update.From
        )


def telegram_eval_gif_generation(update: Update, context: CallbackContext, picture):
    im_bytes = update.message.photo[-1].get_file().download_as_bytearray()

    im_file = BytesIO(im_bytes)  # convert image to file-like object
    im1 = Image.open(im_file)   # img is now PIL Image object
    im2 = Image.open('assets/' + picture)

    gif = generate_gif(im1, im2)

    update.message.reply_document(gif)


def whatsapp_eval_gif_generation(client, update: WhatsAppUpdate, context, picture):
    import requests
    import time
    import boto3
    import os

    from configparser import ConfigParser
    config = ConfigParser()
    config.read("config.ini")

    session = boto3.session.Session()
    s3_client = session.client('s3',
                               region_name=config["space"]["region_name"],
                               endpoint_url=config["space"]["endpoint_url"],
                               aws_access_key_id=os.getenv('SPACES_KEY'),
                               aws_secret_access_key=os.getenv('SPACES_SECRET'))

    if update.MediaUrl0:
        im1_bytes = requests.get(
            update.MediaUrl0, allow_redirects=True).content

        im1_file = BytesIO(im1_bytes)  # convert image to file-like object
        im1 = Image.open(im1_file)   # img is now PIL Image object

        im2_bytes = requests.get(config["assets"]["url"] +
                                 "/" + picture).content
        im2_file = BytesIO(im2_bytes)  # convert image to file-like object
        im2 = Image.open(im2_file)

        gif = generate_gif(im2, im1)

        time_str = str(round(time.time() * 1000))

        s3_client.put_object(Bucket=config["assets"]["bucket"],
                             Key="gif" + "/" + time_str + "_" +
                             str(update.WaId) + '.gif',
                             Body=gif,
                             ACL='public-read',
                             ContentType='image/gif'
                             # Metadata={
                             #    'x-amz-meta-my-key': 'your-value'
                             # }
                             )

        client.messages.create(
            media_url=config["assets"]["url"] + "/gif/" +
            time_str + "_" + str(update.WaId) + '.gif',
            from_=update.To,
            to=update.From
        )


telegram_action_functions = {"eval_gif_generation": telegram_eval_gif_generation,
                             "eval_image_overlay": telegram_eval_image_overlay
                             }

whatsapp_action_functions = {"eval_gif_generation": whatsapp_eval_gif_generation,
                             "eval_image_overlay": whatsapp_eval_image_overlay
                             }
