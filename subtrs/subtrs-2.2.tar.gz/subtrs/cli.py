#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys


def usage(status):
    '''CLI --help menu'''
    args = ['Usage: subtrs [subtitles_file] [destination languages]\n',
            '       Simple tool that trlanslates video subtitles\n',
            '       Support subtitles files [*.sbv, *.vtt, *.srt]',
            '       Destination languages [en,de,ru] etc.\n',
            'Optional arguments:',
            '       --color      View translated text with colour.',
            '       --progress   Show progress bar.',
            '       --export     Export the text only.',
            '  -l,  --languages  Show all supported languages.',
            '  -v,  --version    Print the version and exit.',
            '  -h,  --help       Show this message and exit.',
            ]
    for opt in args:
        print(opt)
    sys.exit(status)
