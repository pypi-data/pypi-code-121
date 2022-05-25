#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import re

# see /samples/bob.*
# replace as smart as possible
# Handle Pass/Splinter
# S before AKQJT will be changed
replacements = [
    (r'([^a-zA-Z])S([^a-zB-IL-PRSU-Z])', r'\1♠\2'),
    (r'([^a-zA-Z])H([^a-zB-IL-PRSU-Z])', r'\1♥\2'),
    (r'([^a-zA-Z])D([^a-zB-IL-PRSU-Z])', r'\1♦\2'),
    (r'([^a-zA-Z])C([^a-zB-IL-PRSU-Z])', r'\1♣\2'),
    (r'黑桃', '♠'),
    (r'红桃', '♥'),
    (r'红心', '♥'),
    (r'方块', '♦'),
    (r'方片', '♦'),
    (r'草花', '♣'),
    (r'梅花', '♣')
]

# support both gb2312 or utf-8 but generated as utf-8 always
def update(txtfile):
    try:
        in_file = open (txtfile, 'r',encoding='utf-8')
        read_lines = in_file.readlines()
    except UnicodeDecodeError as err:
        print(">> open %s as gb2312" % txtfile)
        in_file = open (txtfile, 'r',encoding='gb2312')
        read_lines = in_file.readlines()
    except:
        print("Unexpected error:", sys.exc_info()[0])
        return
    new_txtfile=txtfile+".new"
    with open (new_txtfile, 'w',encoding='utf-8') as out_file:
        for rows in read_lines:
            #print(rows)
            for old, new in replacements:
                rows = re.sub(old,new,rows)
            #print(new_text)
            out_file.write(rows)
        print("> %s is generated" % new_txtfile)

def main():
    # print(sys.argv)
    if len(sys.argv) > 1:
        update(sys.argv[1])
    else:
        print("update4suit.py <file.txt>")

if __name__ == '__main__':
    main()

