#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
from LinuxServerStatsTelegramBot.DI import DI
from LinuxServerStatsTelegramBot.commmand.CpuStats import CpuStats
from LinuxServerStatsTelegramBot.commmand.CronStats import CronStats
from LinuxServerStatsTelegramBot.commmand.DateAndLocation import DateAndLocation
from LinuxServerStatsTelegramBot.commmand.DiskStats import DiskStats
from LinuxServerStatsTelegramBot.commmand.DockerStats import DockerStats
from LinuxServerStatsTelegramBot.commmand.MemoryStats import MemoryStats
from LinuxServerStatsTelegramBot.commmand.CleanMemory import CleanMemory
from LinuxServerStatsTelegramBot.commmand.ServersHealth import ServersHealth
from LinuxServerStatsTelegramBot.core.Invoker import Invoker
from LinuxServerStatsTelegramBot.sender.TelegramSender import TelegramSender

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    logger.info(f"Received command start with {update} in the context: {context}")
    update.message.reply_text("Hi!")


def help(update, context):
    """Send a message when the command /help is issued."""
    help_text = """
    Available commands:
    /cron               : Create a image with Cron stats
    /dateandlocation    : Create a image with Server Date and location
    /disk               : Create a image with Disks stats
    /docker             : Create a image with Docker stats
    /cpu                : Create a image with CPU stats
    /memory             : Create a image with Server Memory stats
    /reports            : Create a zip containing all reports as text files 
    /cleanmemory        : Execute a command to clear the cache and garbage memory 
    /servershealth      : Create a image with the servers health status
    
    """
    update.message.reply_text(help_text)


def cleanmemory(update, context):
    update.message.reply_text("Executing Memory Clean...")
    chat_id = update.message.from_user.id
    DI.set_sender_temporarily(TelegramSender(str(chat_id)))
    Invoker.send_data_as_image(CleanMemory())
    DI.set_original_sender()


def servershealth(update, context):
    update.message.reply_text("Processing Servers Health stats...")
    chat_id = update.message.from_user.id
    DI.set_sender_temporarily(TelegramSender(str(chat_id)))
    Invoker.send_data_as_image(ServersHealth())
    DI.set_original_sender()


def memory(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text("Processing Memory stats...")
    chat_id = update.message.from_user.id
    DI.set_sender_temporarily(TelegramSender(str(chat_id)))
    Invoker.send_data_as_image(MemoryStats())
    DI.set_original_sender()


def cpu(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text("Processing CPU stats...")
    chat_id = update.message.from_user.id
    DI.set_sender_temporarily(TelegramSender(str(chat_id)))
    Invoker.send_data_as_image(CpuStats())
    DI.set_original_sender()


def dateandlocation(update, context):
    """Send a message when the command /help is issued."""
    # u.message.reply_photo()
    update.message.reply_text("Processing Date and Location...")
    chat_id = update.message.from_user.id
    DI.set_sender_temporarily(TelegramSender(str(chat_id)))
    Invoker.send_data_as_image(DateAndLocation())
    DI.set_original_sender()


def cron(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text("Processing Cron Stats...")
    chat_id = update.message.from_user.id
    DI.set_sender_temporarily(TelegramSender(str(chat_id)))
    Invoker.send_data_as_image(CronStats())
    DI.set_original_sender()


def disk(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text("Processing Disk Stats...")
    chat_id = update.message.from_user.id
    DI.set_sender_temporarily(TelegramSender(str(chat_id)))
    Invoker.send_data_as_image(DiskStats())
    DI.set_original_sender()


def docker(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text("Processing Docker stats...")
    chat_id = update.message.from_user.id
    DI.set_sender_temporarily(TelegramSender(str(chat_id)))
    Invoker.send_data_as_image(DockerStats())
    DI.set_original_sender()


def reports(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text("Processing Reports...")
    chat_id = update.message.from_user.id
    DI.set_sender_temporarily(TelegramSender(str(chat_id)))
    Invoker.send_server_stats_as_text()
    DI.set_original_sender()


def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    update.message.reply_text(f"Error : {context.error}")


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(DI.get_tg_bot_token(), use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("memory", memory))
    dp.add_handler(CommandHandler("cpu", cpu))
    dp.add_handler(CommandHandler("dateandlocation", dateandlocation))
    dp.add_handler(CommandHandler("cron", cron))
    dp.add_handler(CommandHandler("disk", disk))
    dp.add_handler(CommandHandler("docker", docker))
    dp.add_handler(CommandHandler("reports", reports))
    dp.add_handler(CommandHandler("cleanmemory", cleanmemory))
    dp.add_handler(CommandHandler("servershealth", servershealth))


    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
