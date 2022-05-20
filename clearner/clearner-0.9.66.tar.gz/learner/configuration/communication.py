# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

import getpass
import os
import sys
import logging

from learner.data_worker.data_loader import get_value


class CommunicationConfiguration:
    """Parse the fields in the communication section of the configuration file."""

    def __init__(self, json_config, credentials):
        self._json_config = json_config
        self._credentials = credentials

        self.admin_email_activate = get_value(self._json_config, False, "communication", "admin_params",
                                              "admin_email_params", "activate")
        self.admin_email_address = self.get_admin_email_address()
        self.admin_email_ausername = self.get_username()
        self.admin_email_password = self.get_password()
        self.admin_email_host = get_value(self._json_config, "smtp.gmail.com", "communication", "admin_params",
                                          "admin_email_params", "host")
        self.admin_email_port = get_value(self._json_config, 587, "communication", "admin_params",
                                          "admin_email_params", "port")

    def get_admin_email_address(self):
        if self.admin_email_activate:
            try:
                admin_email_address = self._json_config["communication"]["admin_params"]["admin_email_params"]["email_address"]
                return admin_email_address
            except KeyError:
                logging.critical("admin_email_params was activated but email_address was not provided. Please update "
                                 "your configuration file and try again. Exiting...")
                sys.exit(1)

    def get_username(self):
        if self.admin_email_activate:
            username = os.getenv("LEARNER_ADMIN_EMAIL_ADDRESS")
            if not username:
                try:
                    username = self._json_config["communication"]["admin_params"]["admin_email_params"]["username"]
                except KeyError:
                    try:
                        username = self._credentials["email"]["username"]
                    except (KeyError, TypeError):  # pragma: no cover
                        username = input("Please enter your email address for sending email: ")
            return username

    def get_password(self):
        if self.admin_email_activate:
            password = os.getenv("LEARNER_ADMIN_EMAIL_PASSWORD")
            if not password:
                try:
                    password = self._json_config["communication"]["admin_params"]["admin_email_params"]["password"]
                except KeyError:
                    try:
                        password = self._credentials["email"]["password"]
                    except (KeyError, TypeError):  # pragma: no cover
                        password = getpass.getpass(prompt="Please enter your password for sending emails: ")
            return password
