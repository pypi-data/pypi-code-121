# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""The main module for handling the communications. This module instantiates email and other communication classes and
calls their driver method to perform the communications."""
from learner.configuration.configuration import Configuration


class CommunicationHandler:
    """Instantiate appropriate objects and call the communicator methods to handle the communications"""

    def __init__(self, conf: Configuration, data=None, message=None):
        """Accept a conf object, data, and message to instantiate the object.

        :param conf: an instance of the Configuration class
        :param data: the data to use for communication purposes
        :param message: the message (typically text) to use for the communication
        """
        self._conf = conf
        self._data = data
        self._message = message

    @property
    def conf(self):
        return self._conf

    @property
    def data(self):
        return self._data

    @property
    def message(self):
        return self._message

    def handle_admin_communication(self):
        """Depending on the parameters, import the relevant class, instantiate the object and call the drive method.

        :return: None
        """
        if self._conf.communication.admin_email_activate:
            from learner.communication.email_manager import AdminEmailManager
            communication_manager = AdminEmailManager(self._conf, message=self.message, data=None)
            communication_manager.handle_communications()
