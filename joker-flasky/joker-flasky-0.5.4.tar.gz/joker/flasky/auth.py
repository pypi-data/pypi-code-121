#!/usr/bin/env python3
# coding: utf-8

import functools
import hashlib
import re
import time
from typing import Optional
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

import flask
import flask.sessions
# noinspection PyPackageRequirements
import itsdangerous
from flask import Flask, Request
# noinspection PyPackageRequirements
from itsdangerous import TimestampSigner, BadSignature
from volkanic import errors

from joker.flasky import viewutils
from joker.flasky.viewutils import RequestBoundSingletonMeta


def _make_salt():
    return hex(int(time.time() * 65555))[-10:][::-1]


class HashedPassword:
    def __init__(self, digest: str, algo: str, salt: str):
        self.digest = digest
        self.algo = algo
        self.salt = salt

    @classmethod
    def parse(cls, hp_string: str):
        digest, algo, salt = hp_string.split(':')
        return cls(digest, algo, salt)

    @classmethod
    def generate(cls, password: str, algo: str = 'sha256', salt: str = None):
        if salt is None:
            salt = _make_salt()
        p = password.encode('utf-8')
        s = salt.encode('utf-8')
        h = hashlib.new(algo, p + s)
        return cls(h.hexdigest(), algo, salt)

    def __str__(self):
        return '{}:{}:{}'.format(self.digest, self.algo, self.salt)

    def verify(self, password: str):
        hp1 = self.generate(password, self.algo, self.salt)
        return self.digest == hp1.digest


class ExtendableSessionInterface(flask.sessions.SecureCookieSessionInterface):
    def _get_session_string(self, app, request):
        return request.cookies.get(self.get_cookie_name(app))

    def open_session(self, app: Flask, request: Request) \
            -> Optional[flask.sessions.SecureCookieSession]:
        """
        Almost identical to
        `flask.sessions.SecureCookieSessionInterface.open_session()`
        except for calling `self._get_session_string()` instead of
        get the session string directly from `request.cookies`.
        """
        ss = self.get_signing_serializer(app)
        if ss is None:
            return None
        # different from flask.sessions.SecureCookieSessionInterface:
        # val = request.cookies.get(self.get_cookie_name(app))
        val = self._get_session_string(app, request)
        if not val:
            return self.session_class()
        max_age = int(app.permanent_session_lifetime.total_seconds())
        try:
            data = ss.loads(val, max_age=max_age)
            return self.session_class(data)
        except itsdangerous.BadSignature:
            return self.session_class()


class LoginInterfaceBase(metaclass=RequestBoundSingletonMeta):
    _user_id_session_key = 'user_id'
    _not_logged_in_message = 'You are not logged-in.'

    def __init__(self, user_id, user_info=None):
        self.user_id = user_id
        self.user_info = user_info

    @staticmethod
    def _get_default_user_id():
        return

    @classmethod
    def get_current_user_id(cls):
        if user_id := flask.session.get('user_id'):
            return user_id
        elif user_id := cls._get_default_user_id():
            return user_id
        else:
            raise errors.BusinessError(cls._not_logged_in_message)

    @classmethod
    def check(cls):
        return cls(cls.get_current_user_id())

    @classmethod
    def login_required(cls, func):
        """Decorate a view function to ensure user logged-in."""

        @functools.wraps(func)
        def _func(*args, **kwargs):
            cls.get_current_user_id()
            return func(*args, **kwargs)

        return _func

    @classmethod
    def login(cls, user_id):
        flask.session[cls._user_id_session_key] = user_id
        return cls(user_id)

    @classmethod
    def logout(cls):
        flask.session.pop(cls._user_id_session_key)

    @staticmethod
    def serialize_current_session():
        return viewutils.serialize_current_session()

    @staticmethod
    def guess_name_type(login_name):
        if re.match(r'\+?\d+[\d-]+', login_name):
            return 'phone'
        # xxxxx@xxxxx.xxx => an email address
        elif re.match(
                r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$',
                login_name):
            return 'email'


class URLPathSigner:
    def __init__(self, secrets, max_age=None):
        self.timed_signer = TimestampSigner(secrets, salt=b'joker-flasky!')
        self.max_age = max_age

    def sign(self, url: str):
        u = urlparse(url)
        signed_path = self.timed_signer.sign(u.path).decode()
        _, t, s = signed_path.rsplit('.', maxsplit=2)
        query = dict(parse_qsl(u.query))
        query['sig'] = f'{t}.{s}'
        u = u._replace(query=urlencode(query))
        return urlunparse(u)

    def verify(self, url: str, sig: str = None) -> bool:
        u = urlparse(url)
        if sig is None:
            query = dict(parse_qsl(u.query))
            sig = query.get('sig', '')
        signed_path = f'{u.path}.{sig}'
        try:
            self.timed_signer.unsign(signed_path, max_age=self.max_age)
        except BadSignature:
            return False
        return True


__all__ = [
    'HashedPassword', 'LoginInterfaceBase',
    'ExtendableSessionInterface', 'URLPathSigner',
]
