#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import re
import markdown
from .xin2pbn import xin2pbn
from .pbn2html import pbn2html

# it is to 
# 1. generate html from markdown
# 2. generate related pbn html output (separately now)
# 2. update color for heart/diamond

replacements = [
    (r'href="http://www.xinruibridge.com/deallog/', r'href="https://isoliu.gitlab.io/deallog/'),
    (r'♠', r'<span class="bcspade" style="color: black">♠</span>'),
    (r'♣', r'<span class="bcclub" style="color: black">♣</span>'),
    (r'♥', r'<span class="bchearts" style="color: red">♥</span>'),
    (r'♦', r'<span class="bcdiamonds" style="color: red">♦</span>'),
    (r'◆', r'<span class="bcdiamonds" style="color: red">♦</span>')
]
# sed -i 's/href="http:\/\/www.xinruibridge.com\/deallog/target="_blank" href="https:\/\/isoliu.gitlab.io\/deallog/g' contents/[0-2]*.html
# sed -i 's/♠/<span class="bchearts" style="color: black">♠<\/span>/g' contents/[0-2]*.html
def update_html(orig_htmlfile, htmlfile):
    try:
        in_file = open(orig_htmlfile, 'r',encoding='utf-8')
        read_lines = in_file.readlines()

        with open (htmlfile, 'w',encoding='utf-8') as out_file:
            for rows in read_lines:
                #print(rows)
                for old, new in replacements:
                    rows = re.sub(old,new,rows)
                #print(new_text)
                out_file.write(rows)
            print(">> %s is generated" % htmlfile)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        return

# markdown to html
def generate_html(mdfile, htmlfile):
    try:
        with open(mdfile, 'r', encoding='utf-8') as f:
            text = f.read()
            html = markdown.markdown(text)

        with open(htmlfile, 'w', encoding='utf-8') as f:
            print(">> %s is generated" % htmlfile)
            f.write(html)
    except UnicodeDecodeError as err:
        print("please save file as utf-8" % mdfile)

# support both gb2312 or utf-8 but generated as utf-8 always
def convert(mdfile):
    if not mdfile.endswith(".md"):
        print("only accept bridge article with .md suffix")
        return
    base_file = mdfile[:-len("md")]
    orig_htmlfile = base_file + "orig.html"
    htmlfile = base_file + "html"
    pbnfile = base_file + "pbn"
    pbnhtmlfile = base_file + "pbn.html"
    # generate raw html from md
    generate_html(mdfile,orig_htmlfile)
    # updtae link and color of suit
    update_html(orig_htmlfile, htmlfile)
    # generate one big pbn only
    xin2pbn.generate_pbn_from_html([htmlfile])
    # generate pbn html file
    pbn2html.pbn2html(pbnfile)

def main():
    # print(sys.argv)
    if len(sys.argv) > 1:
        convert(sys.argv[1])
    else:
        print("zyj2convert.py <file.md>")

if __name__ == '__main__':
    main()
