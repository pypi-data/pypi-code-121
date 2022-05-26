# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import os


class AppSettings:

    AXDD_PERSON_CLIENT_ENV = os.getenv('AXDD_PERSON_CLIENT_ENV',
                                       default='localdev')

    UW_PERSON_DB_USERNAME = os.getenv('DATABASE_USERNAME',
                                      default='postgres')
    UW_PERSON_DB_PASSWORD = os.getenv('DATABASE_PASSWORD',
                                      default='postgres')
    UW_PERSON_DB_DATABASE = os.getenv('DATABASE_DB_NAME', default='postgres')
    UW_PERSON_DB_HOSTNAME = os.getenv('DATABASE_HOSTNAME',
                                      default='localhost')
    UW_PERSON_DB_PORT = os.getenv('DATABASE_PORT', default='5432')

    def get(self, attr):
        return getattr(AppSettings, attr)
