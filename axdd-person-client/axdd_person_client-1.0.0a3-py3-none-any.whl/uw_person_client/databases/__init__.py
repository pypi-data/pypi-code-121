# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from sqlalchemy.orm.session import sessionmaker


class AbstractDatabase(object):

    def __init__(self, expire_session_on_commit=True):
        self._session_factory = sessionmaker(
            expire_on_commit=expire_session_on_commit)
        self._session = None
        self.create_engine()

    def create_engine(self):
        raise NotImplementedError()

    @property
    def session(self):
        if self._session is None:
            self._session = self._session_factory(bind=self.engine)
        return self._session

    def commit_session(self):
        try:
            self.session.commit()
        except Exception as e:
            logging.error(e)
            self.session.rollback()
            raise
