# -*- coding: UTF-8 -*-
import configparser
import os
import re

# 文件编码
FILE_ENCODE = 'UTF-8'
CONFIG = configparser.ConfigParser()

def Parse(path):
    global CONFIG
    # 这些相当于是参数的默认值
    return CONFIG.read(path, encoding=FILE_ENCODE)
    
def Get_fileserver():
    if 'FILESERVER' in CONFIG:
        return dict(CONFIG['FILESERVER'])
    else:
        raise Exception('FILESERVER not in CONFIG!')

def Get_uploadserver():
    if 'UPLOADSERVER' in CONFIG:
        return dict(CONFIG['UPLOADSERVER'])
    else:
        raise Exception('UPLOADSERVER not in CONFIG!')

def Get_database():
    if 'DATABASE' in CONFIG:
        return dict(CONFIG['DATABASE'])
    else:
        raise Exception('DATABASE not in CONFIG!')
        
    # DICTIONARY = set()
    # if 'DICTIONARY' in CONFIG['DEFAULT']:
    #     DICTIONARY = set(readlist(os.path.join(os.path.dirname(__file__), CONFIG['DEFAULT']['DICTIONARY'])))


    # if 'DATABASE' in CONFIG['DEFAULT']:
    #     MAX_ERROR_TIMES_PERTAG_PERTYPE_CSV = int(CONFIG['DEFAULT']['MAX_ERROR_TIMES_PERTAG_PERTYPE_CSV'])

    # if 'PROXY' in CONFIG['DEFAULT']:
    #     MAX_LENGTH_PERTAG = int(CONFIG['DEFAULT']['MAX_LENGTH_PERTAG'])

    # if 'REALTIME' in CONFIG['DEFAULT']:
    #     MAX_LENGTH_PERTAG = int(CONFIG['DEFAULT']['MAX_LENGTH_PERTAG'])

    # return CONFIG['DEFAULT'], DICTIONARY, PATTERNS, MAX_ERROR_TIMES_PERTAG_PERTYPE, MAX_ERROR_TIMES_PERTAG_PERTYPE_CSV, MAX_LENGTH_PERTAG


    # PATTERNS = []
    # for field in CONFIG:
    #     if field == 'DEFAULT':
    #         continue
    #     if 'mode' not in CONFIG[field]:
    #         continue
    #     t = {}
    #     t['name'] = field
    #     t['mode'] = CONFIG[field]['mode']
    #     t['stat'] = CONFIG[field]['stat']
    #     t['patterns'] = []
    #     t['escapes']  = []
    #     t['escape_pfx'] = []
    #     t['escape_sfx'] = []
    #     for item in CONFIG[field]:
    #         if item.startswith('__pattern__'):
    #             if os.path.isfile(os.path.join(os.path.dirname(__file__), CONFIG[field][item])):
    #                 dictionary = readlist(os.path.join(os.path.dirname(__file__), CONFIG[field][item]))
    #                 dictionary = [trans_reserve(i) for i in dictionary]
    #                 t['patterns'].append(re.compile(" |".join(dictionary)))
    #             else:
    #                 t['patterns'].append(re.compile(CONFIG[field][item]))
    #         if item.startswith('__escape__'):
    #             t['escapes'].append(re.compile(CONFIG[field][item]))
    #         if item.startswith('__escape_pfx__'):
    #             t['escape_pfx'].append(re.compile(CONFIG[field][item]))
    #         if item.startswith('__escape_sfx__'):
    #             t['escape_sfx'].append(re.compile(CONFIG[field][item]))
    #     PATTERNS.append(t)
