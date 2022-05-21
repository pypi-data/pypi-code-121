# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
#
# Copyright 2008-2021 Neongecko.com Inc. | All Rights Reserved
#
# Notice of License - Duplicating this Notice of License near the start of any file containing
# a derivative of this software is a condition of license for this software.
# Friendly Licensing:
# No charge, open source royalty free use of the Neon AI software source and object is offered for
# educational users, noncommercial enthusiasts, Public Benefit Corporations (and LLCs) and
# Social Purpose Corporations (and LLCs). Developers can contact developers@neon.ai
# For commercial licensing, distribution of derivative works or redistribution please contact licenses@neon.ai
# Distributed on an "AS IS” basis without warranties or conditions of any kind, either express or implied.
# Trademarks of Neongecko: Neon AI(TM), Neon Assist (TM), Neon Communicator(TM), Klat(TM)
# Authors: Guy Daniels, Daniel McKnight, Regina Bloomstine, Elon Gasper, Richard Leeds
#
# Specialized conversational reconveyance options from Conversation Processing Intelligence Corp.
# US Patents 2008-2021: US7424516, US20140161250, US20140177813, US8638908, US8068604, US8553852, US10530923, US10530924
# China Patent: CN102017585  -  Europe Patent: EU2156652  -  Patents Pending
from threading import Thread

from socketIO_client import SocketIO


class SocketIOCompat(SocketIO):
    def __init__(self, *args, **kwargs):
        super(SocketIOCompat, self).__init__(*args, **kwargs)

    def emit(self, event, data, namespace=None, callback=None):
        """
        Adapts the new syntax expected by socketio.client to the legacy socketio_client package
        """
        if isinstance(data, list) or isinstance(data, tuple):
            super().emit(event, *data, path=namespace, callback=callback)
        elif isinstance(data, dict):
            super().emit(event, **data, path=namespace, callback=callback)
        else:
            super().emit(event, data, path=namespace, callback=callback)

    def send(self, data, namespace=None, callback=None):
        super().send(data, callback, path=namespace)

    def connect(self, url):
        super().connect()

    def _run_listener(self):
        self.wait()

    def run_forever(self):
        event_thread = Thread(target=self._run_listener)
        event_thread.setDaemon(True)
        event_thread.start()
