# -*- coding:utf-8 -*-

import argparse
import logging
import os
import sys

from com.dvsnier.config.journal.common_config import config
from com.dvsnier.email import DEBUGGER, ENVIRONMENT_VARIABLE_CONFIGURATION, VERSIONS
from com.dvsnier.email.email import Email


def execute(args=None):
    ''' the execute command '''
    if args is None:
        args = sys.argv[1:]
    #
    # the reference link:
    #
    #   1. https://docs.python.org/zh-cn/3/library/argparse.html
    #
    parser = argparse.ArgumentParser(
        prog='dvs-email',
        description='this is a simple email execution program,\
         only a single email address can be mailed.',
        epilog='the copyright belongs to DovSnier that reserve the right of final interpretation.\n',
    )
    parser.add_argument('-V', '--version', action='version', version=VERSIONS, help='the show version and exit.')
    parser.add_argument('-v',
                        '--verbose',
                        action='store_true',
                        default=False,
                        dest='verbose',
                        help='if true, prepare to output detailed journal records, otherwise no.')
    parser.add_argument('-cfg',
                        '--config-file',
                        action='store',
                        metavar='config-file',
                        dest='config_file',
                        help='the current mail configuration file.')
    parser.add_argument('-mr',
                        '--mail-receiver',
                        action='store',
                        metavar='mail-receiver',
                        dest='mail_receiver',
                        help='the current mail recipient.')
    parser.add_argument('-ra',
                        '--receiver-alias',
                        action='store',
                        metavar='receiver-alias',
                        dest='receiver_alias',
                        help='the current mail recipient alias.')
    parser.add_argument(
        '-f',
        '--mode-flag',
        action='store_false',
        default=True,
        dest='mode_flag',
        help='if flags == true, email program is ssl mode, otherwise no, and the default value is True.')
    parser.add_argument('-s',
                        '--subject',
                        action='store',
                        type=str,
                        metavar='subject',
                        dest='subject',
                        help='the current email subject and the default value is None \
             when It is recommended that users fill in the email subject by themselves.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-msg',
                       '--message',
                       action='extend',
                       nargs='+',
                       type=str,
                       metavar='message',
                       dest='message',
                       help='the current email message and the default value is None.')
    group.add_argument('-mf',
                       '--message-file',
                       action='store',
                       type=argparse.FileType('r'),
                       metavar='message-file',
                       dest='message_file',
                       help='the current email message file.')
    args = parser.parse_args(args)
    run(args)


def run(args):
    ''' the run script command '''
    if args and args.verbose:
        kwargs = {'output_dir_name': 'dvs-email', 'file_name': 'log', 'level': logging.DEBUG}
        config(kwargs)
    email = Email()  # type: Email
    user = os.path.expanduser('~')
    dvs_rc = os.path.join(user, ENVIRONMENT_VARIABLE_CONFIGURATION)
    if os.path.exists(dvs_rc):
        email.config_file(dvs_rc)
        logging.info('the currently found user({}) environment variable definition configuration file.'.format(user))
    if args:
        if DEBUGGER:
            # print('vars(args): {}'.format(vars(args)))
            # logging.warning('the current config(args): {}'.format(json.dumps(vars(args), indent=4)))
            logging.warning('the current config(args): {}'.format(vars(args)))
        if args.config_file:
            email.config_file(args.config_file)
        if args.mail_receiver:
            email.get_config().set_mail_receiver(args.mail_receiver)
        if args.receiver_alias:
            email.get_config().set_receiver_alias(args.receiver_alias)
        if not args.subject:
            logging.warning('the current message subject format does not meet the requirements.')
        if args.message_file:
            with args.message_file as amf:
                values = amf.readlines()
                email.init(args.mode_flag).builderText(args.subject, ''.join(values)).sendmail().quit()
        else:
            content = None
            if args.message:
                if isinstance(args.message, list):
                    content = ' '.join(args.message)
                elif isinstance(args.message, str):
                    content = args.message
                else:
                    # nothing to do
                    pass
            if content:
                email.init(args.mode_flag).builderText(args.subject, content).sendmail().quit()
                pass


if __name__ == "__main__":
    '''the main function entry'''
    execute()
