from urllib.request import Request, urlopen

import requests

from ..tools.logger import Logger


def download_web(url, filename):
    """ 下载网页 """
    try:
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        req = Request(url=url, headers=headers)
        content = urlopen(req).read().decode("utf-8")
        if len(content) > 0:
            with open(filename, 'w') as fw:
                fw.write(content)
        return True
    except Exception as e:
        print(e)
        return False

def get_web_text(url):
    """获取网页文本"""
    try:
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        req = Request(url=url, headers=headers)
        content = urlopen(req).read().decode("utf-8")
        return content
    except Exception as e:
        print(e)
        return ""

def get_github_star(url):
    """获取github标星数量 以及 上次提交时间 很容易被封"""
    req = Request(url=url)
    content = urlopen(req).read().decode("utf-8")
    star_num = content.split("users starred this repository")[0].split("\"")[-1].strip()
    star_num = int(star_num)

    last_time = content.split('<relative-time datetime="')[1].split("T")[0]
    return star_num, last_time

def youdao_translate(word):
    """ 使用有道词典翻译 """

    try:
        url = f'http://dict.youdao.com/w/{word}/#keyfrom=dict2.top'
        text_list = requests.get(url=url).text.split('<ul>')[1].split('</ul>')[0].split('<li>')[1:]
        item_list = []
        for text in text_list:
            item = text.split('</li>')[0].strip()
            if '人名' in item:
                continue
            item_list.append(item)
        return item_list
    
    except Exception:
        Logger.warn('没有翻译结果 或者 出现网络故障!')
        return []


def parse_google_text(web_text):
    """ 解析谷歌学术页面源码 """

    paper_list = []
    title_set = set()
    for text in web_text.split('data-cid'):
        segs = text.split('data-clk-atid')
        if len(segs) != 3:
            continue
        title = segs[-1].split('</a>')[0].split('">')[1].replace('<b>', ' ').replace('</b>', ' ').strip()

        if title in title_set:
            continue
        title_set.add(title)

        pdf_url = text.split('tabindex')[-1].split('<a href="')[1].split('"')[0]

        cite_num = 0
        if '被引用次数：' in text:
            cite_num = text.split('被引用次数：')[1].split('</a>')[0]
            cite_num = int(cite_num)

        paper_list.append(
            {
                "title": title,
                "cite_num": cite_num,
                "pdf_url": pdf_url,
            }
        )

    return paper_list
