#!/usr/bin/env python3
# -*- coding: utf-8 -*-

name = 'weibo_2_album'

import cached_url
import yaml
from bs4 import BeautifulSoup
from telegram_util import AlbumResult as Result
from telegram_util import getWid, matchKey
import sys
import os
import hashlib
from PIL import Image
import warnings
warnings.filterwarnings('ignore')

prefix = 'https://m.weibo.cn/statuses/show?id='

def urlShouldRemove(url):
	return matchKey(url, ['video.weibo.com', '/openapp', 'feature/applink', 'weibo.com/tv', 'miaopai.', 'm.weibo.cn/p/index?extparam='])

def getRetweetCap(json):
	json = json.get('retweeted_status')
	if not json:
		return ''
	longText = json.get('longText', {}).get('longTextContent')
	if not longText:
		return json['text']
	for item in json.get('longText', {}).get('url_objects', []):
		ori = item['url_ori']
		to_replace = item.get('info', {}).get('url_long')
		if to_replace:
			if urlShouldRemove(to_replace):
				to_replace = ''
			if matchKey(to_replace, ['http://weibo.com/p/']): # remove if text is link, weibo place
				to_replace = ''
			longText = longText.replace(ori, to_replace)
	return longText

def isprintable(s):
    try: 
    	s.encode('utf-8')
    except UnicodeEncodeError: return False
    else: return True

def getPrintableForHash(s):
	return ''.join(x for x in s if isprintable(x)).replace('转发微博', '').replace('投稿人', '')

def getPrintableForProd(s):
	return s.encode('utf-16', 'surrogatepass').decode('utf-16').replace('转发微博', '').replace('投稿人', '')

def isLongPic(path):
	ext = os.path.splitext(path)[1] or '.html'
	cache = 'tmp/' + cached_url.getFileName(path) + ext
	img = Image.open(cache)
	w, h = img.size
	return h > w * 2.1

def getHash(json):
	text = getPrintableForHash(json['text'] + '\n\n' + getRetweetCap(json)).replace('转发微博', '')
	b = BeautifulSoup(text, features="lxml")
	return ''.join(b.text[:10].split()) + '_' + hashlib.sha224(b.text.encode('utf-8')).hexdigest()[:10]

def cleanupCap(text):
	text = getPrintableForProd(text).strip()
	soup = BeautifulSoup(text, features="html.parser")
	result = []
	for item in soup:
		if item.name == 'br':
			result.append('\n')
			continue
		if item.name == None:
			result.append(str(item).replace('<', '&lt;').replace('>', '&gt;'))
			continue
		if item.name == 'a':
			link = item.get('href')
			if urlShouldRemove(link):
				continue
			if (not link or matchKey(link, ['weibo.cn/p', 'weibo.cn/search', 'weibo.com/show']) 
					or item.text[:1] == '@'):
				result.append(item.text)
				continue
			result.append('<a href="%s">%s</a>' % (link, item.text))
	text = ''.join(result).strip()
	text = text.replace('\n', '\n\n')
	for _ in range(5):
		text = text.replace('\n\n\n', '\n\n')
	return text.strip()

def removeName(comment):
	ind = comment.find(':')
	if ind > 0:
		return comment[ind + 1:]
	return comment

def toCommentMode(text):
	comments = text.split('//@')
	if not comments:
		return ''
	comments = [comments[0]] + [removeName(comment) for comment in comments[1:]]
	comments = [comment for comment in comments[::-1] if len(comment) > 10]
	if not comments:
		return ''
	return '\n\n' + '\n\n'.join(['【网评】' + comment for comment in comments])

def getCap(json):
	main_text = cleanupCap(json['text'])
	retweet_text = cleanupCap(getRetweetCap(json))
	if not retweet_text:
		return main_text
	if not main_text:
		return retweet_text
	return retweet_text + toCommentMode(main_text)

# should put to some util package, 
# but I don't want util to be dependent on cached_url
def isAnimated(path): 
	cached_url.get(path, force_cache=True, mode='b')
	gif = Image.open(cached_url.getFilePath(path))
	try:
		gif.seek(1)
	except EOFError:
		return False
	else:
		return True

def enlarge(url):
	candidate = url.replace('orj360', 'large')
	candidate_content = cached_url.get(candidate, mode='b', force_cache = True)
	if (0 < len(candidate_content) < 1 << 22 or isLongPic(candidate) or 
		isAnimated(candidate)):
		return candidate
	return url
	
def getImages(json):
	return [enlarge(x['url']) for x in json.get('pics', [])]

def getVideo(json):
	return json.get('page_info', {}).get('media_info', {}).get(
		'stream_url_hd', '')

def getUserInfo(user_info):
	if not user_info:
		return ''
	screen_name = user_info.get('screen_name')
	user_id = user_info.get('id', '')
	if not screen_name:
		return ''
	return '<a href="https://m.weibo.cn/u/%s">%s</a> %s' % (user_id, screen_name, user_id)

def getAdditionalInfo(json):
	result = ''
	video = getVideo(json) or getVideo(json.get('retweeted_status', {}))
	if video: 
		result += '%s ' % video
	try:
		imgs = ([x['url'] for x in json.get('pics', [])] or 
			[x['url'] for x in json.get('retweeted_status', {}).get('pics', [])])
	except:
		imgs = []
	if imgs:
		if len(imgs) > 1:
			result += 'imgs(%d): %s ' % (len(imgs), imgs[0])
		else:
			result += '%s ' % imgs[0]
	user_info = getUserInfo(json.get('user', {}))
	if user_info:
		result += 'user: %s ' % user_info
	retweeted_user_info = getUserInfo(json.get('retweeted_status', {}).get('user', {}))
	if retweeted_user_info:
		result += 'retweeted_from: %s ' % retweeted_user_info
	return result.strip()

def get(path, json=None):
	wid = getWid(path)
	r = Result()
	if not json:
		try:
			json = yaml.load(cached_url.get(prefix + wid), Loader=yaml.FullLoader)
			json = json['data']
		except:
			return r
	if 'test' in sys.argv:
		with open('tmp/%s.json' % wid, 'w') as f:
			f.write(str(json))
	r.imgs = getImages(json) or getImages(json.get('retweeted_status', {}))
	r.cap_html = json['text']
	r.title = json.get('status_title')
	r.cap_html_v2 = getCap(json)
	r.video = getVideo(json) or getVideo(json.get('retweeted_status', {}))
	r.wid = json.get('id')
	r.rwid = json.get('retweeted_status', {}).get('id', '')
	r.hash = getHash(json)
	r.url = path
	return r