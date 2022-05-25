import json
from typing import Optional
import requests
import logging


class Level(object):
    ACTIVE = 'active'
    TIME_SENSITIVE = 'timeSensitive'
    PASSIVE = 'passive'


class Sound(object):
    ALARM = 'alarm.caf'
    ANTICIPATE = 'anticipate.caf'
    BELL = 'bell.caf'
    BIRDSONG = 'birdsong.caf'
    BLOOM = 'bloom.caf'
    CALYPSO = 'calypso.caf'
    CHIME = 'chime.caf'
    CHOO = 'choo.caf'
    DESCENT = 'descent.caf'
    ELECTRONIC = 'electronic.caf'
    FANFARE = 'fanfare.caf'
    GLASS = 'glass.caf'
    GOTOSLEEP = 'gotosleep.caf'
    HEALTHNOTIFICATION = 'healthnotification.caf'
    HORN = 'horn.caf'
    LADDER = 'ladder.caf'
    MAILSEND = 'mailsend.caf'
    MINUET = 'minuet.caf'
    MULTIWAYINVITATION = 'multiwayinvitation.caf'
    NEWMAIL = 'newmail.caf'
    NEWSFLASH = 'newsflash.caf'
    NOIR = 'noir.caf'
    PAYMENTSUCCESS = 'paymentsuccess.caf'
    SHAKE = 'shake.caf'
    SHERWOODFOREST = 'sherwoodforest.caf'
    SPELL = 'spell.caf'
    SUSPENSE = 'suspense.caf'
    TELEGRAPH = 'telegraph.caf'
    TIPTOES = 'tiptoes.caf'
    TYPEWRITERS = 'typewriters.caf'
    UPDATE = 'update.caf'
    SILENCE = 'silence.caf'


class Bark:
    server = "https://api.day.app"

    def __init__(self, server: Optional[str] = None, keys=None):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        if server:
            self.server = server
        if not keys or len(keys) == 0:
            raise ValueError("keys must be specified")
        self.keys = keys

    @staticmethod
    def is_blank(line):
        return not line or len(line) == 0

    def get_request_url(self, content, key, title: Optional[str] = None, group: Optional[str] = None,
                        url=None, is_archive: Optional[bool] = False, level=None, sound=None,
                        automatically_copy: Optional[bool] = False,
                        copy: Optional[str] = None, icon: Optional[str] = None):
        base_url = '{server}/{key}'.format(server=self.server, key=key)
        if title:
            base_url += '/{title}'.format(title=title)
        base_url += '/{}'.format(content)

        params = {
            'group': None if Bark.is_blank(group) else group,
            'level': None if Bark.is_blank(level) else level,
            'automaticallyCopy': 1 if automatically_copy else None,
            'copy': copy if automatically_copy and copy else None,
            'url': None if Bark.is_blank(url) else url,
            'sound': None if Bark.is_blank(sound) else sound,
            'isArchive': 1 if is_archive else None,
            'icon': None if Bark.is_blank(icon) else icon
        }
        return base_url, params

    def push(self, content, title=None, url=None, group=None, receivers=None, is_archive=None,
             level=None, sound=None, automatically_copy=False, copy: Optional[str] = None,
             icon=None):
        failing_receiver = []
        for key in (receivers or self.keys):
            base_url, params = self.get_request_url(
                content=content, key=key, title=title,
                group=group, url=url, is_archive=is_archive,
                level=level, sound=sound,
                automatically_copy=automatically_copy,
                copy=copy, icon=icon
            )
            self.logger.info("Push to {}".format(base_url))

            resp = requests.get(base_url, params=params)
            data = json.loads(resp.text)
            if not (resp.status_code == 200 and data['code'] == 200):
                self.logger.error("Fail to push to [{}], error message = {}".format(key, data['message']))
                failing_receiver.append(key)

        self.logger.info("Number of failed pushes: {}".format(len(failing_receiver)))
        return failing_receiver

