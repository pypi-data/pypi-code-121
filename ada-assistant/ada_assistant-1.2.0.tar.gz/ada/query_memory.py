from __future__ import print_function
# -*- coding: utf-8 -*-

import calendar
import hashlib
import json
import os
import re
import time
from ada.txt_editor import LineFixedTxtEditor, InteractivePrompt
from getpass import getpass
from Crypto.Cipher import Blowfish

'''
let ada remember either a file, a string and peek the remembered content
for peek, ada will print LINE_BUFFER_SIZE lines above N_MORE_LINES_TO_PRINT lines below
around the regex keyword (case insensitive);
if no keyword provided, ada will show all the content

layout of config:
{file_alias0: file_path0, file_alias1: file_path1, ...}
'''
GREEN_CODE = u"\033[0;32m"
RED_CODE = u"\033[0;31m"
RESET_CODE = u"\033[0;0m"

START_LINE = ">>>>>>>>>>>>>>>>>>>>>>>>>>"
END_LINE = "<<<<<<<<<<<<<<<<<<<<<<<<<<"

LINE_BUFFER_SIZE = 10
N_MORE_LINES_TO_PRINT = 10

# default TTL is 15 days
DEFAULT_TTL = 15
DAY_SECONDS = 3600 * 24

_, col = os.popen('stty size', 'r').read().split()
EDITOR_WIDTH = int(col) - 1

CONFIG_PATH = os.path.expanduser('~/.adaconfig/.config')
MEMORY_PATH = os.path.expanduser('~/.adaconfig/.memory')
PWD_BLOCK_SIZE = 8
PWD_HEADING = "pwdbook:"

def process_memory(*args):
    try:
        # check if the config dir exists
        if os.path.exists(CONFIG_PATH):
            # load config json
            fp = open(CONFIG_PATH, 'r')
            config = json.load(fp)
            fp.close()
        else:
            os.makedirs(os.path.expanduser('~/.adaconfig'))
            fp = open(MEMORY_PATH, 'w')
            fp.close()
            # initilize the config json
            config = {"_memory": MEMORY_PATH}

        if 'peek' in args:
            idx = args.index('peek')
            peek(config, *args[idx + 1:])
        elif 'remember' in args:
            idx = args.index('remember')
            if idx == len(args) - 1:
                ed1 = LineFixedTxtEditor(EDITOR_WIDTH, [''])
                ctt = ed1.run()
                txt = ctt[0][0]
                ed2 = InteractivePrompt(EDITOR_WIDTH, "ttl (days): ")
                ctt2 = ed2.run()
                ttl_str = ctt2[0][0].replace(' ', '')
                try:
                    if len(ttl_str) > 0:
                        ttl = int(ttl_str)
                    else:
                        ttl = DEFAULT_TTL
                except Exception:
                    print("unrecognized ttl string {}, using default ttl {}".format(ttl_str, DEFAULT_TTL))
                    ttl = DEFAULT_TTL
                remember(config, txt, ttl)
            elif idx == len(args) - 2:
                remember(config, args[idx + 1])
            else:
                remember(config, args[idx + 1], int(args[-1]))
        elif 'register' in args:
            idx = args.index('register')
            if idx + 2 > len(args) - 1:
                print('to register, specify <alias> <file_path>')
                return
            register(config, args[idx + 1], args[idx + 2])
        elif 'forget' in args:
            idx = args.index('forget')
            if idx >= len(args) - 1:
                print('forget what?')
                return
            if args[idx + 1] in config:
                config.pop(args[idx + 1], None)
            else:
                # try deleting hash in _memory
                for hash in args[idx + 1:]:
                    forget(config, hash)
        elif 'config' in args:
            print(config)
        elif 'amend' in args:
            idx = args.index('amend')
            if len(args) - 1 < idx + 1:
                print('to amend, specify <hash> [<new_content>]')
            elif len(args) - 1 == idx + 1:
                hash = args[idx + 1]
                ret = forget(config, hash)
                if ret[1] <= 0:
                    print("hash not found, update nothing")
                else:
                    editor = LineFixedTxtEditor(EDITOR_WIDTH, [ret[2]])
                    ctt = editor.run()
                    editor = InteractivePrompt(EDITOR_WIDTH, "new ttl (days): ")
                    ctt2 = editor.run()
                    ttl_str = ctt2[0][0].replace(' ', '')
                    try:
                        if len(ttl_str) > 0:
                            ttl = int(ttl_str)
                        else:
                            ttl = ret[1]
                    except Exception:
                        print("unrecognized ttl string {}, using original ttl {}".format(ttl_str, ret[1]))
                        ttl = ret[1]
                    remember(config, '\n'.join(ctt[0]), ttl, ret[0])
            else:
                hash = args[idx + 1]
                new_content = ' '.join(args[idx + 2:])
                ret = forget(config, hash)
                if ret[1] <= 0:
                    print("hash not found, create new entry")
                    remember(config, new_content)
                else:
                    remember(config, new_content, ret[1], ret[0])
        elif 'append' in args:
            idx = args.index('append')
            if len(args) - 1 < idx + 2:
                print('to amend, specify <hash> <content_to_append>')
            else:
                hash = args[idx + 1]
                new_content = ' '.join(args[idx + 2:])
                ret = forget(config, hash)
                if ret[1] <= 0:
                    print("hash not found, append to nothing")
                else:
                    remember(config, ret[-1] + new_content, ret[1], ret[0])
        elif 'pwd' in args:
            idx = args.index('pwd')
            if len(args[idx+1:]) == 0:
                print('no action under pwd')
            else:
                pwd(config, *args[idx+1:])
        else:
            print("I don't understand the input" + ' '.join(args))
            return
        # flush the config, return
        fp = open(CONFIG_PATH, 'w')
        json.dump(config, fp)
    except Exception as e:
        print(e)


'''
args can be:
1. <empty>: showing all memory
2. [<alias/file/dir>]: showing all content in alias/file/dir
3. [<alias/file/dir> <regex>]: showing the adjacent lines around regex matches
4. [<regex>]: showing all memory that matches regex
'''
def peek(config, *args):
    # case 1
    if len(args) == 0:
        if os.path.exists(config['_memory']):
            with open(config['_memory'], 'r') as fp:
                entries = json.load(fp)
            MEMFORMAT = (GREEN_CODE + "[{} {}] " + RESET_CODE + "{} " + RED_CODE + "(expires in {} hrs)" + RESET_CODE)
            for entry in entries:
                ts = time.localtime(entry[0])
                time_str = "{}-{}-{} {}:{}:{}".format(
                    ts.tm_year,
                    str(ts.tm_mon).rjust(2, '0'),
                    str(ts.tm_mday).rjust(2, '0'),
                    str(ts.tm_hour).rjust(2, '0'),
                    str(ts.tm_min).rjust(2, '0'),
                    str(ts.tm_sec).rjust(2, '0'))
                now = calendar.timegm(time.gmtime())
                if entry[3] * DAY_SECONDS - (now - entry[0]) > 0:
                    print(MEMFORMAT.format(time_str, entry[2], transformBulletsView(entry[1]), "{:.2f}".format((entry[3] * DAY_SECONDS - (now - entry[0])) / 3600.0)))
    # case 2 or 3
    # TODO(yuquanshan): refactor code to two functions: _process_file and _process_dir
    elif args[0] in config or os.path.exists(os.path.expanduser(args[0])):
        # case 2
        good = False
        if len(args) == 1:
            if args[0] in config:
                with open(config[args[0]], 'r') as fp:
                    print(fp.read(), end="")
                    good = True
            else:
                path = os.path.expanduser(args[0])
                if os.path.exists(path):
                    if os.path.isfile(path):
                        with open(path, 'r') as fp:
                           print(fp.read(), end="")
                        good = True
                    elif os.path.isdir(path):
                        file_paths = [os.path.join(path, p) for p in os.listdir(path) if os.path.isfile(os.path.join(path, p))]
                        for p in file_paths:
                            print(RED_CODE + "<{}>".format(p)+ RESET_CODE)
                            with open(p, 'r') as fp:
                                print(fp.read(), end="")
                        good = True
            if not good:
                print("ERROR:" + str(args[0]) + "is neither a registered alias nor a valid path to a file or dir")
        # case 3
        else:
            pattern = u".*{}.*".format(args[1]).lower()
            print(RED_CODE + u"SEARCH PATTERN (case insensitive): " + pattern + RESET_CODE)
            if args[0] in config:
                with open(config[args[0]], 'r') as fp:
                    lines = fp.readlines()
                    print_match(lines, pattern)
                    good = True
            else:
                path = os.path.expanduser(args[0])
                if os.path.exists(path):
                    if os.path.isfile(path):
                        with open(path, 'r') as fp:
                            lines = fp.readlines()
                            print_match(lines, pattern)
                            good = True
                    elif os.path.isdir(path):
                        file_paths = [os.path.join(path, p) for p in os.listdir(path) if os.path.isfile(os.path.join(path, p))]
                        for p in file_paths:
                            print(RED_CODE + "<{}>".format(p)+ RESET_CODE)
                            with open(p, 'r') as fp:
                                lines = fp.readlines()
                                print_match(lines, pattern)
                                good = True
            if not good:
                print("ERROR:" + str(args[0]) + "is neither a registered alias nor a valid path to a file or dir")
    # case 4
    else:
        with open(config['_memory'], 'r') as fp:
            pattern = u".*{}.*".format(args[0]).lower()
            print(RED_CODE + u"SEARCH PATTERN (case insensitive): " + pattern + RESET_CODE)
            entries = json.load(fp)
        lines = []
        for entry in entries:
            lines.append(entry[1] + '\n')
        print_match(lines, pattern)


def remember(config, s, ttl = DEFAULT_TTL, ts = None):
    entries = []
    if os.path.exists(config['_memory']):
        with open(config['_memory'], 'r') as f:
            if len(f.read()) > 0:
                f.seek(0)
                entries = json.load(f)
    if not ts:
        ts = calendar.timegm(time.gmtime())
    buffered_entries = []
    hash = hashlib.sha224(s.encode()).hexdigest()[:6]
    hash_set = set()
    for entry in entries:
        tdelta = ts - entry[0]
        if tdelta > entry[3] * DAY_SECONDS:
            # ttl passed, forget this entry
            continue
        else:
            hash_set.add(entry[2])
            if hash in hash_set:
                print("WARNING: hash collides with an exising content, replace it with the new one")
                continue
            buffered_entries.append(entry)
    buffered_entries.append([ts, s, hash, ttl])
    with open(config['_memory'], 'w') as f:
        json.dump(buffered_entries, f)


# forget a _memory entry in hash, return [ts, ttl, original_content] ,
# if ttl <= 0, then either the entry is expired or non-existing
def forget(config, hash):
    entries = []
    ret = [0, 0, '']
    if os.path.exists(config['_memory']):
        with open(config['_memory'], 'r') as f:
            if len(f.read()) > 0:
                f.seek(0)
                entries = json.load(f)
    buffered_entries = []
    for entry in entries:
        ety = entry
        if ety[2] == hash:
            # if hash matches, forget by not adding to buffered_entries
            ret = [ety[0], ety[-1], ety[1]]
            continue
        else:
            buffered_entries.append(ety)
    with open(config['_memory'], 'w') as f:
        json.dump(buffered_entries, f)
    return ret


def register(config, alias, fp):
    if not os.path.exists(os.path.expanduser(fp)):
        raise Exception("File " + fp + " doesn't exist")
    config[alias] = fp


def pwd(config, action, *args):
    pwd = getpass('Enter you password: ')
    crypt = Blowfish.new(pwd)
    # schema: pwdbook:{name: [uname, pwd, comment]...}
    pwd_list = {}
    if '_pwd' not in config:
        print("please register _pwd first")
    if os.path.exists(config['_pwd']):
        with open(config['_pwd'], 'rb') as f:
            txt = f.read()
            if len(txt) >= PWD_BLOCK_SIZE:
                txt = crypt.decrypt(txt).decode('ASCII')
                if PWD_HEADING not in txt:
                    raise Exception('Wrong password: ' + pwd)
                txt = txt.replace(PWD_HEADING, '', 1).strip()
                pwd_list = json.loads(txt)
    if action == 'search':
        if len(args) == 0:
            print('nothing to peek')
            return
        kw = args[0]
        found = False
        for i in pwd_list.items():
            if kw in i[0].lower():
                found = True
                print("{}: {}".format(i[0], i[1]))
        if not found:
            print(kw + ' not found')
    elif action == 'update':
        if len(args) < 3:
            print('please at least specify name, uname, and pwd')
            return
        name = args[0]
        ctnt = args[1:]
        pwd_list[name] = ctnt
    elif action == 'delete':
        if len(args) == 0:
            print('nothing to delete')
            return
        if args[0] not in pwd_list:
            print('cannot find ' + args[0])
            return
        del pwd_list[args[0]]
    txt = json.dumps(pwd_list)
    txt = str(PWD_HEADING)+txt
    txt = txt.ljust((len(txt) // PWD_BLOCK_SIZE  + 1) * PWD_BLOCK_SIZE)
    etxt = crypt.encrypt(txt)
    with open(config['_pwd'], 'wb') as f:
        f.write(etxt)


def print_match(lines, pattern):
    line_buffer = []
    match_in_buffer = False
    more_lines_countdown = 0
    line_count = 0
    for l in lines:
        line_count = line_count + 1
        l = l
        match = re.match(pattern, l.lower())
        if match:
            match_in_buffer = True
            more_lines_countdown = N_MORE_LINES_TO_PRINT
            line_buffer.append(GREEN_CODE + l + RESET_CODE)
        elif match_in_buffer:
            line_buffer.append(l)
            more_lines_countdown = more_lines_countdown - 1
            if more_lines_countdown == 0:
                print(START_LINE)
                for i in line_buffer:
                    print(i, end="")
                print(END_LINE + u"(line: {})".format(line_count))
                line_buffer = line_buffer[-LINE_BUFFER_SIZE:]
                match_in_buffer = False
        else:
            if len(line_buffer) == LINE_BUFFER_SIZE:
                line_buffer.pop(0)
            line_buffer.append(l)
    if match_in_buffer:
        print(START_LINE)
        for i in line_buffer:
            print(i, end="")
        print(END_LINE + u"(line: {})".format(line_count))


def transformBulletsView(s):
    l = re.compile("[0-9]+\. ").split(s)
    for i in range(1, len(l)):
        l[i] = u"\n   \u2022 " + l[i]
    if len(l) > 1:
        l[0] = '\n' + l[0]
        l[-1] = l[-1] + '\n'
    return ''.join(l)
