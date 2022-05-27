#!/usr/bin/env python3
import argparse
import datetime
import json
import re
import sys
import time
from operator import itemgetter
from urllib.parse import urlsplit
from xml.dom import minidom


def baseurl(href):
    split = urlsplit(href)
    scheme = '%s://' % split.scheme if split.scheme else ''
    return '%s%s' % (scheme, split.netloc)

def get_in(obj, *keys):
    for i, k in enumerate(keys, 1):
        rest = keys[i:]
        v = None
        if k == ':':
            return [get_in(e, *rest) for e in obj]
        try: v = itemgetter(k)(obj)
        except: pass
        if v is None: return None
        obj = v
    return obj

def sget_in(obj, *keys):
    r = get_in(obj, *keys)
    if r is None: return ''
    return str(r).strip()

def text_to_html(s):
    html = re.sub('(\s)(https?://[^\s]+)', '\\1<a href="\\2" target="_blank">\\2</a>', s)
    return html.replace('\n', '<br/>')

DATE_FORMATS = [
    '%Y-%m-%dT%H:%M:%SZ',  # 2022-05-19T13:54:20Z
    '%Y-%m-%dT%H:%M:%S%z', # 2022-05-19T13:54:20-05:00
    '%d.%m.%Y %H:%M:%S',   # 19.05.2022 13:54:20
    '%Y-%m-%dT%H:%M:%S%z', # 2022-05-19T13:54:20-05:00
    '%a, %d %b %Y %H:%M:%S %z (%Z)',
    '%Y-%m-%dT%H:%M:%S.%f',
    '%Y-%m-%d %H:%M:%S',
    '%Y-%m-%d',
    '%Y%m%d',
]
now = datetime.datetime.now()
def date2rss(datestr):
    dt = None
    for f in DATE_FORMATS:
        try:
            dt = datetime.datetime.strptime(datestr, f)
            break
        except: pass
    if datestr and not dt:
        print("cannot parse date '%s'" % datestr, file=sys.stderr)
    dt = dt or now
    tup = time.mktime(dt.timetuple())
    return time.strftime('%a, %d %b %Y %H:%M:%S %z', time.localtime(tup))

def parse_authors(data):
    if isinstance(data, list):
        return ', '.join(parse_authors(author) for author in data)
    elif isinstance(data, dict):
        return sget_in(data, 'name')
    elif isinstance(data, str):
        return data


def el(doc, name, attrs=None, text=None, cdata=None, children=None):
    e = doc.createElement(name)
    for k,v in (attrs or {}).items(): e.setAttribute(k, v)
    if cdata: e.appendChild(doc.createCDATASection(cdata))
    if text: e.appendChild(doc.createTextNode(text))
    if children and isinstance(children, list):
        for c in children: e.appendChild(c)
    return e

def create_rss(metadata, items):
    doc = minidom.Document()
    title = sget_in(metadata, 'title')
    description = sget_in(metadata, 'description')
    feed_url = sget_in(metadata, 'feed_url') or sget_in(metadata, 'url') or '#'
    home_url = sget_in(metadata, 'home_page_url') or (baseurl(feed_url) if feed_url else '') or '#'

    rss = el(doc, 'rss', {
        'version': '2.0',
        'xmlns:atom': 'http://www.w3.org/2005/Atom',
        'xmlns:itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
        'xmlns:media': 'http://search.yahoo.com/mrss/' 
    })
    doc.appendChild(rss)

    channel = el(doc, 'channel')
    rss.appendChild(channel)

    channel.appendChild(el(doc, 'atom:link', {
        'href': feed_url,
        'rel': 'self',
        'type': 'application/rss+xml'
    }))
    channel.appendChild(el(doc, 'title', text=title))
    if description: channel.appendChild(el(doc, 'description', text=description))
    channel.appendChild(el(doc, 'link', text=home_url))
    channel.appendChild(el(doc, 'generator', text='json2rss'))

    for i in items:
        item_url = get_in(i, 'url') or \
                   get_in(i, 'link') or \
                   get_in(i, 'webpage_url') or \
                   sget_in(i, 'href')
        if not item_url: continue
        item_title = sget_in(i, 'title') or item_url
        item_desc = sget_in(i, 'content_html') or \
            text_to_html(sget_in(i, 'content_text') or sget_in(i, 'description'))
        item_guid = sget_in(i, 'guid') or sget_in(i, 'id') or item_url
        item_image = sget_in(i, 'image') or sget_in(i, 'thumbnail')
        if item_image:
            item_desc = '<img align="right" hspace="5" src="%s"/>' % item_image + item_desc
        item_date = sget_in(i, 'date_published') or sget_in(i, 'pub_date') or sget_in(i, 'date')
        item_author = parse_authors(get_in(i, 'author') or get_in(i, 'authors'))
        item = el(doc, 'item', children=[
            el(doc, 'guid', text=item_guid),
            el(doc, 'link', text=item_url),
            el(doc, 'title', text=item_title),
            el(doc, 'description', cdata=item_desc),
        ])
        if item_date: item.appendChild(el(doc, 'pubDate', text=date2rss(item_date)))
        if item_author: item.appendChild(el(doc, 'author', text=item_author))
        if item_image: item.appendChild(el(doc, 'media:thumbnail', {'url':item_image}))
        if 'duration' in i: item.appendChild(el(doc, 'itunes:duration', text=sget_in(i, 'duration')))
        channel.appendChild(item)
    xml_str = doc.toprettyxml(indent='  ')
    return xml_str

def parse_input():
    input_lines = list(sys.stdin.readlines())
    out = []
    try:
        return json.loads(''.join(input_lines))
    except json.decoder.JSONDecodeError:
        pass
    for line in input_lines:
        try:
            out.append(json.loads(line))
        except json.decoder.JSONDecodeError:
            pass
    return out

def normalize(data):
    items = []
    if isinstance(data, list):
        return {}, data
    if 'items' in data:
        items = get_in(data, 'items') or []
        del data['items']
    return data, items

def json2rss(title, url, feed):
    j = parse_input()
    if not j:
        print('incorrect input', file=sys.stderr)
        sys.exit(1)
    metadata, items = normalize(j)
    metadata['title'] = title or sget_in(metadata, 'title')
    metadata['home_page_url'] = url or sget_in(metadata, 'home_page_url')
    metadata['feed_url'] = feed or sget_in(metadata, 'feed_url')
    print(create_rss(metadata, items))

def main():
    parser = argparse.ArgumentParser(description='Convert JSON to RSS feed')
    parser.add_argument('-t', '--title', type=str, help='feed title', default='')
    parser.add_argument('-u', '--url', type=str, help='website url', default='')
    parser.add_argument('-f', '--feed', type=str, help='feed url', default='')
    args = parser.parse_args()
    json2rss(args.title, args.url, args.feed)

if __name__ == '__main__':
    main()
