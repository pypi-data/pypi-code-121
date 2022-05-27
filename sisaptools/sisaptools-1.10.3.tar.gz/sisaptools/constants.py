# -*- coding: utf8 -*-

"""
Constants per utilitzar a utils.
"""

import os
import sys


IS_PYTHON_3 = sys.version_info[0] == 3
TMP_FOLDER = os.environ.get('TMP_FOLDER', '/tmp')
APP_CHARSET = os.environ.get('APP_CHARSET', 'latin1')

if APP_CHARSET == 'utf8':
    MARIA_CHARSET = 'utf8mb4'
    MARIA_COLLATE = 'utf8mb4_bin'
    os.environ['NLS_LANG'] = '.UTF8'
elif APP_CHARSET == 'latin1' or APP_CHARSET == 'cp1252':
    MARIA_CHARSET = 'latin1'
    MARIA_COLLATE = 'latin1_general_ci'
    os.environ['NLS_LANG'] = '.WE8ISO8859P1'
else:
    raise AttributeError('APP_CHARSET {} not supported'.format(APP_CHARSET))

MARIA_STORAGE = 'MyISAM'
os.environ['NLS_DATE_FORMAT'] = 'YYYYMMDD'

SECTORS_ECAP = ("6102", "6209", "6211", "6310", "6416", "6519", "6520", "6521",
                "6522", "6523", "6625", "6626", "6627", "6728", "6731", "6734",
                "6735", "6837", "6838", "6839", "6844", "6951")
