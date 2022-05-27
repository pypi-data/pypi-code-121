import datetime
import re
from newspaper import Article
import html
import hashlib
import scrapy


class ArticleItem(scrapy.Item):
    task_id = scrapy.Field()
    domain_url = scrapy.Field()
    domain_id = scrapy.Field()
    domain_name = scrapy.Field()
    source_url = scrapy.Field()
    source_id = scrapy.Field()
    source_name = scrapy.Field()
    block_id = scrapy.Field()
    title = scrapy.Field()
    publish_date = scrapy.Field()
    url = scrapy.Field()
    retweeted_url = scrapy.Field()
    url_md5 = scrapy.Field()
    author = scrapy.Field()
    content = scrapy.Field()
    article_html = scrapy.Field()
    images = scrapy.Field()
    oss_images = scrapy.Field()
    movies = scrapy.Field()
    oss_movies = scrapy.Field()
    other_info = scrapy.Field()
    upload_oss = scrapy.Field()
    download_video = scrapy.Field()
    download_image = scrapy.Field()
    created_date = scrapy.Field()
    crawl_comment = scrapy.Field()
    comment_total_count = scrapy.Field()
    err_msg = scrapy.Field()


class ArticleCommentItem(scrapy.Item):
    task_id = scrapy.Field()
    domain_url = scrapy.Field()
    domain_id = scrapy.Field()
    domain_name = scrapy.Field()
    post_url = scrapy.Field()
    post_id = scrapy.Field()
    block_id = scrapy.Field()
    comment_id = scrapy.Field()
    url = scrapy.Field()
    url_md5 = scrapy.Field()
    like_count = scrapy.Field()
    author = scrapy.Field()
    content = scrapy.Field()
    article_html = scrapy.Field()
    other_info = scrapy.Field()
    upload_oss = scrapy.Field()
    publish_date = scrapy.Field()
    created_date = scrapy.Field()


def get_item(response, source, block, parse=True, uploadOss=True, crawlComment=False):
    item = ArticleItem()
    item["domain_url"] = block["domain_url"]
    item["domain_id"] = block["domain_id"]
    item["domain_name"] = block["domain_name"]
    item["block_id"] = block["identification"]
    item["upload_oss"] = uploadOss
    item["crawl_comment"] = crawlComment
    if source:
        item["source_url"] = source["url"]
        item["source_id"] = source["identification"]
        item["source_name"] = source["name"]
        item["upload_oss"] = source.get('upload_oss', False)
        item["crawl_comment"] = source.get('crawl_comment', False)
    if response:
        item["url"] = response.url
        item["url_md5"] = hashlib.md5(response.url.encode("utf-8")).hexdigest()
    if parse:
        content_regex = block.get('content_regex')
        if content_regex and len(content_regex) > 0:
            manual_parse(item, response, content_regex)
        else:
            auto_parse(item, response)
    return item


def get_comment_item(response, post_result, block, uploadOss=True):
    item = ArticleCommentItem()
    item["domain_url"] = block["domain_url"]
    item["domain_id"] = block["domain_id"]
    item["domain_name"] = block["domain_name"]
    item["block_id"] = block["identification"]
    item["upload_oss"] = uploadOss
    if post_result:
        item["post_url"] = post_result["url"]
        item["post_id"] = post_result["_id"]
        item["upload_oss"] = post_result.get('upload_oss', False)
    if response:
        item["url"] = response.url
        item["url_md5"] = hashlib.md5(response.url.encode("utf-8")).hexdigest()
    return item


def __get_content_html(response, base_url, path):
    html_res = __get_content_extract(response, path)
    if html_res and "" != html_res:
        return get_h5_html(response.url, base_url, html_res)
    return None


def __get_content_text(response, path):
    content_res = __get_content_extract(response, 'string({})'.format(path))
    if content_res and "" != content_res:
        return get_h5_content(content_res)
    return None


def __get_content_images(response, path):
    image_path3 = "{}/descendant::img/@data-echo".format(path)
    images_list3 = response.xpath(image_path3).extract()
    images_list3 = list(map(handle_img_set, list(images_list3)))
    images3 = get_img_list(response, images_list3)

    image_path1 = "{}/descendant::img/@src".format(path)
    images_list1 = response.xpath(image_path1).extract()
    images1 = get_img_list(response, images_list1)

    image_path2 = "{}/descendant::img/@srcset".format(path)
    images_list2 = response.xpath(image_path2).extract()
    images_list2 = list(map(handle_img_set, list(images_list2)))
    images2 = get_img_list(response, images_list2)

    image_path4 = "{}/descendant::img/@data-src".format(path)
    images_list4 = response.xpath(image_path4).extract()
    images4 = get_img_list(response, images_list4)

    item_list = list(set(images1 + images2 + images3 + images4))
    return item_list


def __get_content_videos(response, path):
    movie_path = "{}/descendant::video/@src".format(path)
    movie_list = response.xpath(movie_path).extract()
    movie_last = get_video_list(response, movie_list)
    return movie_last


def add_images(response, item, images):
    images = get_img_list(response, images)
    if images and len(images) > 0:
        if 'images' in item and len(item['images']) > 0:
            item['images'] = item['images'] + images
        else:
            item['images'] = images


def add_videos(response, item, videos):
    videos = get_video_list(response, videos)
    if videos and len(videos) > 0:
        if 'movies' in item and len(item['movies']) > 0:
            item['movies'] = item['movies'] + videos
        else:
            item['movies'] = videos


def manual_parse(item, response, content_regex):
    base_index = response.url.find('/', 8)
    if base_index >= 0:
        base_url = response.url[:base_index]
    else:
        base_url = response.url
    title_path = content_regex.get("title_path")
    if title_path:
        item["title"] = __get_content_extract(response, title_path)
    content_path = content_regex.get("content_path")
    if content_path:
        item['article_html'] = __get_content_html(response, base_url, content_path)
        item['content'] = __get_content_text(response, content_path)
        images = __get_content_images(response, content_path)
        item['images'] = images
        item['movies'] = __get_content_videos(response, content_path)

    content_list = content_regex.get("content_list")
    if content_list and len(content_list) > 0:
        for content_item in content_list:
            name = content_item.get('name')
            path = content_item.get('path')
            if name == "article_html":
                item['article_html'] = __get_content_html(response, base_url, path)
            if name == "content":
                item['content'] = __get_content_text(response, path)
            if name == "images":
                images = __get_content_images(response, path)
                if images:
                    add_images(response, item, images)
            if name == "movies":
                movies = __get_content_videos(response, path)
                if movies:
                    add_videos(response, item, movies)
            if name == "image":
                image = __get_content_extract(response, path)
                if image and '' != image:
                    add_images(response, item, [image])
            if name == "movie":
                movie = __get_content_extract(response, path)
                if movie and '' != movie:
                    add_videos(response, item, [movie])
    publish_path = content_regex.get("publish_path")
    date_format_list = content_regex.get("date_format_list")
    if publish_path and date_format_list:
        date_str = __get_content_extract(response, publish_path)
        item['publish_date'] = get_date(date_str, date_format_list)

    author = {}
    author_name_path = content_regex.get("author_name_path")
    if author_name_path:
        author["name"] = __get_content_extract(response, author_name_path)
    author_avatar_path = content_regex.get("author_avatar_path")
    if author_avatar_path:
        avatar_url = __get_content_extract(response, author_avatar_path)
        author["avatar"] = response.urljoin(avatar_url)
    item['author'] = author

    other_info = {}
    other_paths = content_regex.get("other_paths")
    if other_paths and len(other_paths) > 0:
        for other_path in other_paths:
            name = other_path["name"]
            path = other_path["path"]
            other_info[name] = __get_content_extract(response, path)
    item["other_info"] = other_info


def get_date(date_str, date_strip_list):
    date = None
    for date_strip in date_strip_list:
        try:
            if date_strip == "s":
                s = int(date_str)
                date = datetime.datetime.fromtimestamp(s)
            elif date_strip == "ms":
                ms = int(date_str) / 1000.0
                date = datetime.datetime.fromtimestamp(ms)
            else:
                date = datetime.datetime.strptime(date_str, date_strip)
        except:
            pass
        if date:
            break
    return date


def handle_img_set(image):
    if not image and False == isinstance(image, str):
        return image
    index = image.find(" ")
    if index > 0:
        return image[:index]
    return image


def auto_parse(item, response):
    article = Article(response.url, language='zh', keep_article_html=True, fetch_images=False)
    article.set_html(response.text)
    article.parse()
    authors = list(article.authors)
    item['title'] = article.title
    if len(authors) > 0:
        item['author'] = {
            "name": authors
        }
    item['publish_date'] = article.publish_date
    item['article_html'] = html.unescape(article.article_html)
    item['images'] = list(article.images)
    item['movies'] = list(article.movies)
    item['content'] = article.text
    return item


def __get_content_extract(response, path):
    text = response.xpath(path).extract_first()
    if text:
        return text.replace('\xa0', ' ').strip()
    return text


# 获取文字内容，去重回车空格
def get_h5_content(content):
    if not content or content == "":
        return content
    pattern1 = re.compile('( |\t){2,}')
    pattern2 = re.compile('((\r\n|\n)(\s)*){2,}')
    pattern3 = re.compile('<[^>]+/>')
    pattern4 = re.compile('<[^>]+(([\s\S])*?)<\/[^>]+>')
    content = re.sub(pattern1, " ", content)
    content = re.sub(pattern2, "\r\n", content)
    content = re.sub(pattern3, "\r\n", content)
    content = re.sub(pattern4, "\r\n", content)
    return content


# 获取Html 链接为全路径
def get_h5_html(url, base_url, htmlText):
    url_path = None
    url_host = base_url
    nPos = url.rfind('/') + 1
    if nPos > 0:
        url_path = url[:nPos]
    htmlText = re.sub('style="display:none;"', '', htmlText)
    htmlText = re.sub('<style(((?!>).)*)>(((?!</style>)[\s\S])*)</style>', '', htmlText)
    htmlText = re.sub('<script(((?!>).)*)>(((?!</script>)[\s\S])*)</script>', '', htmlText)
    image_list = re.findall(r'<img(((?!>).)*)data-echo="(((?!").)*)"(((?!>).)*)>', htmlText)
    for image_item in image_list:
        url = image_item[2]
        htmlText = re.sub(r'<img(((?!>).)*)data-echo="%s"(((?!>).)*)>' % url, '<img src="%s">' % url, htmlText)
    if url_path:
        pattern1 = re.compile('(href="(?!http|/|./|../|javascript))|(href="./)')
        pattern3 = re.compile('(src="(?!http|/|./|../|javascript))|(src="./)')
        htmlText = re.sub(pattern1, 'href="%s' % url_path, htmlText)
        htmlText = re.sub(pattern3, 'src="%s' % url_path, htmlText)
        nPrePos = url[:(nPos - 1)].rfind('/')
        if nPrePos >= 10:
            url_pre_path = url[:(nPrePos + 1)]
            patternHref = re.compile('href="../')
            patternSrc = re.compile('href="../')
            htmlText = re.sub(patternHref, 'href="%s' % url_pre_path, htmlText)
            htmlText = re.sub(patternSrc, 'src="%s' % url_pre_path, htmlText)

    if url_host:
        if url_host[len(url_host) - 1] != '/':
            url_host += "/"
        pattern2 = re.compile('href="/')
        pattern4 = re.compile('src="/')
        htmlText = re.sub(pattern2, 'href="%s' % url_host, htmlText)
        htmlText = re.sub(pattern4, 'src="%s' % url_host, htmlText)
    return htmlText


# 获取链接列表
def get_img_list(response, images):
    regex = r'^(https|http)(.*)(jpg|png|jpeg)'
    if not images or len(images) <= 0:
        return images
    img_res = []
    for image in images:
        image = response.urljoin(image)
        if image:
            matchObj = re.search(regex, image, re.I)
            if matchObj:
                img_res.append(image)
    return img_res


def get_video_list(response, videos):
    regex = r'^(https|http)(.*)(jpg|png|jpeg)'
    if not videos or len(videos) <= 0:
        return videos
    video_res = []
    for video in videos:
        video = response.urljoin(video)
        if video:
            matchObj = re.search(regex, video, re.I)
            if matchObj is None:
                video_res.append(video)
    return video_res


def get_json_item(json_item, item_regex):
    if item_regex is None or json_item is None:
        return None
    item_regex_list = item_regex.split('.')
    if len(item_regex_list) > 0:
        res_item = json_item
        for item_regex_item in item_regex_list:
            res_item = res_item.get(item_regex_item)
            if res_item is None:
                return None
        return res_item
    return None


def set_json_item(json_obj, item_regex, val):
    if item_regex is None or json_obj is None:
        return
    item_regex_list = item_regex.split('.')
    if len(item_regex_list) > 0:
        res_item_list = []
        json_item = json_obj
        last_regex_item = None
        for item_regex_item in item_regex_list:
            res_item_list.append({
                'id': last_regex_item,
                'item': json_item
            })
            json_item = json_item.get(item_regex_item)
            if json_item is None:
                json_item = {}
            last_regex_item = item_regex_item
        else:
            res_item_list.append({
                'id': last_regex_item,
                'item': str(val)
            })
        res_item_list.reverse()
        last_item = None
        last_key = None
        for res_item_item in res_item_list:
            id = res_item_item.get('id')
            item = res_item_item.get('item')
            if last_key is not None and last_item is not None:
                item[last_key] = last_item
            last_item = item
            last_key = id
            if last_key is None:
                break
        return last_item
