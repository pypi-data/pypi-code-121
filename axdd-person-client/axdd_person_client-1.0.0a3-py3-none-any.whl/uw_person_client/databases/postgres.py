# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from commonconf import settings
from sqlalchemy import create_engine
from uw_person_client.databases import AbstractDatabase


URL_PATTERN = \
    "postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"


class Postgres(AbstractDatabase):

    def create_engine(self):
        url = URL_PATTERN.format(
            username=getattr(settings, "UW_PERSON_DB_USERNAME"),
            password=getattr(settings, "UW_PERSON_DB_PASSWORD"),
            host=getattr(settings, "UW_PERSON_DB_HOSTNAME"),
            port=getattr(settings, "UW_PERSON_DB_PORT"),
            database=getattr(settings, "UW_PERSON_DB_DATABASE")
        )
        self.engine = create_engine(url,
                                    echo=False,
                                    logging_name='sqlalchemy')
