#!/bin/env python3
from slack_cleaner2 import *
import argparse
import logging


def argparser():
    """ Argument parser for the script

    Returns:
        parser: Arguments from the command line
    """
    parser = argparse.ArgumentParser(description='Delete all messages in a channel')
    parser.add_argument('--channel', help='Channel to delete messages from', required=True)
    parser.add_argument('--token', help='Slack token', required=True)
    parser.add_argument('--debug', help='Debug mode', action='store_true', default=False)
    return parser


def logger(debug):
    """ Setup logging

    Args:
        debug (bool):  Debug mode

    Returns:
        logging.Logger: Logger object
    """
    if debug:
        logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='myapp.log',
                    filemode='a')
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)slogger - %(name)s - %(levelname)s - %(message)s')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.debug('Debug mode enabled')
        return logger
    else:
        logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='myapp.log',
                    filemode='a')
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.info('Debug mode NOT enabled')
        return logger


def delete_all_messages_in_channel(channel,debug,s):
    """ Delete all messages in a channel

    Args:
        channel (string): Slack channel to delete messages from
    """
    my_logger = logger(debug)

    my_logger.info('Deleting all messages in channel: ' + channel)
    # delete all general messages and also iterate over all replies
    for msg in s.c.general.msgs(with_replies=True):
        msg.delete()
    my_logger.info('Deleted all generic messages in channel: ' + channel)

    # delete all messages in -bots channels
    for msg in s.msgs(filter(match(channel), s.conversations)):
    # delete messages, its files, and all its replies (thread)
        msg.delete(replies=True, files=True)
    my_logger.info('Deleted all bot messages in channel: ' + channel)

def main():
    """ Main function

    Returns:
        None
    """
    parser = argparser()
    args = parser.parse_args()
    channel = args.channel
    token = args.token
    debug = args.debug
    s = SlackCleaner(token)
    delete_all_messages_in_channel(channel,debug,s)

if __name__ == '__main__':
    main()
