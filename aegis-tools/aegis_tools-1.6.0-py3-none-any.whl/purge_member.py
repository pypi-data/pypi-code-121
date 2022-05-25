#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#
# Purge Member  -  WARNING
#
# Execute a drastic series of delete cascades in order to be able to hard-delete a member row
# THIS IS JUST FOR TESTING NEW MEMBER CODE


# Python Imports
import functools
import logging
import glob
import os
import sys

# To run in scope of ../
path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, path)

# Extern Imports
from tornado.options import define, options

# Project Imports
import config
import stdlib
import database
import model


# Command line options in global scope
define('dry_run', default=True, help="Dry run - make no changes", type=bool)
define('member_id', default=None, help="member_id to delete from system", type=int)
config.initialize()
logging.info("Running purge_member.py   Env: %s   Database: %s   Dry Run: %s   member_id: %s", options.env, options.pg_database, options.dry_run, options.member_id)
if not options.member_id or not int(options.member_id):
    logging.error("Can't delete member_id: %s", options.member_id)
    exit(1)
member_id = int(options.member_id)
# Main
def main():
    try:
        member = model.Member.get_id(member_id)
        if not member:
            logging.error("Can't delete member that doesn't exist")
            exit(1)
        email = model.Email.get_id(member['email_id'])
        logging.warning("Member has email: %s", email['email'])
        if options.dry_run:
            logging.warning("Will EXPUNGE ALL EXISTENCE OF member_id: %s", member_id)
            exit(0)

        cursor = model.db().cursor()
        model.db().execute("UPDATE member SET google_user_id=NULL, email_id=NULL WHERE member_id=%s", member_id, cursor=cursor)
        model.db().execute("UPDATE email SET google_user_id=NULL WHERE email_id=%s", email['email_id'], cursor=cursor)
        model.db().execute("DELETE FROM google_user WHERE member_id=%s", member_id, cursor=cursor)
        model.db().execute("DELETE FROM email WHERE member_id=%s", member_id, cursor=cursor)
        model.db().execute("DELETE FROM user_ WHERE member_id=%s", member_id, cursor=cursor)
        model.db().execute("DELETE FROM member WHERE member_id=%s", member_id, cursor=cursor)
        model.db().commit()
        logging.warning("You just expunged member_id: %s   email: %s", member_id, email['email'])
        
    except Exception as ex:
        logging.exception(ex)
        exit(1)

if __name__ == "__main__":
    main()
