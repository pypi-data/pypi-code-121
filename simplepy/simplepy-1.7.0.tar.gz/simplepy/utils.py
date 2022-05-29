import base64
import json
import os
import random
import re
import socket
import time
import zipfile
from datetime import datetime
from string import ascii_letters
from urllib.parse import unquote_plus, parse_qs, urlsplit
from urllib.request import urlopen

import cv2
import numpy as np
import pandas as pd
import paramiko
import pymongo
import requests
from faker import Faker
from loguru import logger

from simplepy import LIB_PATH
from simplepy.decorators import get_callback_path


def extract_img(text):
    """
    TODO: 获取图片后缀, 提取网页的url

    :param text:
    :return:
    """
    urls = re.findall(r'//(.*?).jpg|.gif｜.jpeg|.png|.JPG|.GIF|.PNG|.JPEG', text, re.I)
    return ['https://' + str(x) + '.jpg' for x in urls if len(x) > 20]


def download_image_decode(src, flag=3):
    """
    下载图片到内存, 生成image对象
    :param src:
    :param flag:
    :return:
    """
    resp = urlopen(src)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, flag)
    return image


def base_download(url):
    """
    返回基础网页信息
    Args:
        url:

    Returns:

    """
    headers = default_headers()
    rep = requests.get(url, headers=headers)
    rep.encoding = rep.apparent_encoding
    return rep.text


def get_timestamp(bit=13):
    """
    返回时间戳
    Args:
        bit:

    Returns:

    """
    if bit == 13:
        return int(round(time.time() * 1000))
    return int(time.time())


def read_content(path):
    """
    读取内容
    Args:
        path:

    Returns:

    """
    with open(path, encoding='utf-8') as f:
        content = f.read()
    return content


def get_random_num(start=1, end=3):
    """
    获取一个随机数
    Args:
        start:
        end:

    Returns:

    """
    return random.choice(range(start, end))


def get_random_time(start=1, end=3):
    """
    赶回一个随机数
    Args:
        start:
        end:

    Returns:

    """
    return time.sleep(random.uniform(start, end))


def extract_json_by_re(content):
    """
    提取 jsonp 返回的json内容
    'sm_1642126166228({"code":1100,"message":"success","requestId":"5df76595f659e51faa6be0d950cee01b","riskLevel":"PASS"})'

    Returns:

    """
    return json.loads(re.search('\((.*?)\)', content, re.I).groups()[0])


def get_today():
    """
    获取当天日期
    Returns:

    """
    return datetime.now().strftime('%Y-%m-%d')


def invalid_char_replace(char: str):
    """
    替换windows不支持的特殊字符
    \/:*?"<>|
    """
    return char.replace('/', '').replace("\\", '').replace(":", '').replace("*", '').replace("?", '').replace('|',
                                                                                                              '').replace(
        '<', '').replace('>', '').replace('"', '')


def delete_html(html):
    """
    去除html标签
    Args:
        html:

    Returns:

    """
    res = re.compile('>(.*?)<')
    text = ''.join(res.findall(html))
    return text


@get_callback_path
def read_txt(name, **kwargs):
    """
    迭代返回数据
    Args:
        name: 只需要传入文件名

    Returns:

    """
    path = kwargs.get('path')
    file_path = os.path.join(path, name)
    with open(file_path, encoding='utf-8') as f:
        while True:
            line = f.readline()
            yield line.replace('\n', '').replace(' ', '')


@get_callback_path
def drop_df(name, cols: list, method='csv', save=True, save_method='csv', **kwargs) -> pd.DataFrame:
    """
    去重返回df
    Args:
        name: 要去重的文件，只需要传入文件名
        cols: 要去重的 dataframe 列 数组传入
        method: csv/excel
        save: 是否保存
        save_method: 保存方式
        **kwargs: 回调注入

    Returns:

    """
    path = kwargs.get('path')
    file_path = os.path.join(path, name)
    if method == 'csv':
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
    df.drop_duplicates(subset=cols, inplace=True)
    if save:
        if save_method == 'csv':
            df.to_csv(f"{os.path.join(path, name)}-drop-done.csv", encoding='utf-8-sig', index=True)
        else:
            df.to_csv(f"{os.path.join(path, name)}-drop-done.xlsx", index=True)
    return df


def split_path(path):
    """
    G:\code\codeline\爬虫\客户爬虫\51job\51.xlsx

    G:\code\codeline\爬虫\客户爬虫\51job   51.xlsx

    Args:
        path: 要拆分的路径

    Returns:

    """
    return os.path.split(path)


def dict_sort(data: dict, reverse=False):
    """
    字典排序 默认升序
    :param data:
    :param reverse
    :return:
    """
    x = dict(list(sorted(data.items(), key=lambda x: x[0], reverse=reverse)))
    return x


@get_callback_path
def csv_save(per: dict, name=None, dataframe=False, **kwargs):
    """
    csv 头治理
    Args:
        per: python dict 字典类型
        name: 要保存的文件名
        dataframe:

    Returns:

    """
    path = kwargs.get('path')
    filename = kwargs.get('filename')
    file_path = os.path.join(path, f"{name if name else filename}.csv")
    if dataframe:
        df = per
    else:
        df = pd.DataFrame([per], dtype='str')
    if os.path.exists(os.path.join(path, f'{name}.csv')):
        df.to_csv(file_path, encoding='utf-8-sig', index=False, header=False, mode='a')
    else:
        df.to_csv(file_path, encoding='utf-8-sig', index=False)


@get_callback_path
def csv2excel(name, **kwargs):
    """
    csv 转 excel
    如果同名csv存在，会在结尾加上 当天日期
    Args:
        name: 要转换的文件名

    Returns:

    """
    path = kwargs.get('path')
    df = pd.read_csv(os.path.join(path, name))
    save_path = f"{os.path.join(path, name)}.xlsx"
    if os.path.exists(save_path):
        df.to_excel(f"{os.path.join(path, name)}-{get_today()}.xlsx", index=False)
    else:
        df.to_excel(f"{os.path.join(path, name)}.xlsx", index=False)


@get_callback_path
def excel2csv(name, **kwargs):
    """
    csv 转 excel
    Args:
       name: csv文件名

    Returns:

    """
    path = kwargs.get('path')
    df = pd.read_csv(os.path.join(path, name))
    save_path = f"{os.path.join(path, name)}.xlsx"
    if os.path.exists(save_path):
        df.to_csv(f"{os.path.join(path, name)}-{get_today()}.csv", index=False, encoding='utf-8-sig')
    else:
        df.to_csv(f"{os.path.join(path, name)}.csv", index=False, encoding='utf-8-sig')


@get_callback_path
def join_table(df1_name: str, df2_name: str, on, how="left", method='excel', save_name=None, **kwargs):
    """
    将两个表进行左右关联合并
    Args:
        df1_name: 文件名
        df2_name: 文件名
        on: 列名
        how: 默认左关联
        method: csv / excel  关联后的存储方式
        save_name: 如果传入将按该文件名保存，否则取脚本的 basename 为名称存储
        **kwargs:

    Returns:

    """
    path = kwargs.get('path')
    filename = save_name if save_name else kwargs.get('filename')
    df1_path = os.path.join(path, df1_name)
    df2_path = os.path.join(path, df2_name)
    df1 = pd.read_excel(df1_path, error_bad_lines=False, engine='python') if df1_path.endswith('xlsx') else pd.read_csv(
        df1_path, error_bad_lines=False, engine='python')
    df2 = pd.read_excel(df2_path, error_bad_lines=False, engine='python') if df2_path.endswith('xlsx') else pd.read_csv(
        df2_path, error_bad_lines=False, engine='python')

    df = pd.merge(df1, df2, how=how, on=on)
    if method == 'excel':
        df.to_excel(f'{os.path.join(path, filename)}.xlsx', index=False)
    else:
        df.to_csv(f"{os.path.join(path, filename)}.csv", index=False, encoding='utf-8-sig')


def merge_table(path, name, suffix=None, drop_col=None, save_method=None, date_format=None):
    """
    合并路径下的dataframe文件，将多个单独的 dataframe 进行合并
    Args:
        path: 文件路径
        name: 需要保存的文件名
        suffix: 要过滤的文件前缀
        drop_col: ['链接']
        save_method: csv/excel
        date_format:  时间$%Y年%m月%d日%H:%M

    Returns:

    """
    data = []
    main_path = os.path.split(path)[0]
    for item in os.listdir(main_path):
        logger.info(item)
        if suffix:
            if item.startswith(suffix):
                full_path = os.path.join(main_path, item)
                df = pd.read_csv(full_path, encoding='utf-8', error_bad_lines=False)
                data.append(df)

        else:
            full_path = os.path.join(main_path, item)
            df = pd.read_csv(full_path, encoding='utf-8', error_bad_lines=False)
            data.append(df)

    contact_df = pd.concat(data, axis=0)
    if drop_col:
        contact_df.drop_duplicates(drop_col, inplace=True)
    if save_method == 'csv':
        contact_df.to_csv(f'{os.path.join(main_path, name)}.csv', index=False, encoding='utf-8-sig')
    else:
        contact_df.to_excel(f'{os.path.join(main_path, name)}.xlsx', index=False)

    # v0.1: 格式化时间
    if date_format:
        col, format_data = date_format.split('$')
        contact_df[col] = pd.to_datetime(contact_df[col], format=format_data)

    return contact_df


def random_str(num):
    """
    生成随机字符串
    Args:
        num: 生成位数

    Returns:

    """
    return ''.join([random.choice(ascii_letters) for _ in range(num)])


def base642bin(path, data):
    """
    base64图片保存为本地图片
    注意前缀：data:image/png;base64,
    Args:
        path: 存储路径
        data: b64数据

    Returns:

    """
    image_bin = base64.b64decode(data)
    with open(os.path.join(path, random_str(6) + '.png'), 'wb+') as f:
        f.write(image_bin)


def t2d(timestamp):
    """
    时间戳转日期
    :param timestamp:
    :return:
    """
    if str(timestamp).__len__() > 10:
        timestamp = int(str(timestamp)[:10])
    timestamp_temp = time.localtime(timestamp)
    return time.strftime("%Y-%m-%d %H:%M:%S", timestamp_temp)


def d2t(t):
    """
    日期转时间戳
    :param t:
    :return:
    """
    datetime_temp = time.strptime(t, "%Y-%m-%d %H:%M:%S")
    return int(time.mktime(datetime_temp))


def random_ua() -> str:
    """
    获取随机UA
    :return:
    """
    ua = Faker()
    return ua.user_agent()


def default_headers(cookie=None, request_type=None, host=None, origin=None, referer=None, ua=True) -> dict:
    """
    默认请求头
    host, origin, referer  依次传入
    :return:
    """
    if request_type == 'form':
        content_type = 'application/x-www-form-urlencoded; charset=utf-8'
    elif request_type == 'json':
        content_type = 'application/json;charset=UTF-8'
    else:
        content_type = None
    headers = {
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "sec-ch-ua-platform": '"Windows"',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.62" if ua else random_ua(),
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": content_type,
        "Accept-Language": "zh-CN,zh-TW;q=0.9,zh;q=0.8,en-US;q=0.7,en;q=0.6",
        "Connection": "keep-alive",
        "Host": host,
        "Origin": origin,
        "Referer": referer,
        "Cookie": cookie
    }
    return {key: value for key, value in headers.items() if value}


def sftp_upload(host, uasername, password, port=22):
    """
    sftp上传
    :return:
    """
    transport = paramiko.Transport((host, port))
    transport.connect(username=uasername, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)

    sftp.put('Windows.txt', '/root/')
    transport.close()


def sftp_download(host, uasername, password, port=22):
    """
    sftp下载
    :return:
    """
    transport = paramiko.Transport((host, port))
    transport.connect(username=uasername, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.get('/root/Linux.txt', 'Linux.txt')
    transport.close()


def split_query_param(url, scheme=False):
    """
    传入查询参数url, 将查询参数字典化
    url = 'https://s.taobao.com/search?data-key=sort&data-value=sale-desc&ajax=true&_ksTS=1639710656177_893&callback=jsonp894&spm=a21bo.jianhua.201867-main.3.5af911d9VlR87A&q=%E5%AE%B6%E5%B1%85&bcoffset=1&ntoffset=7&p4ppushleft=2%2C48'

    Args:
        url: 要拆分的url

    Returns:

    """
    url = unquote_plus(url)
    split_url = urlsplit(url)
    main_url = split_url.scheme
    if scheme:
        return main_url + "://" + split_url.netloc,
    else:
        return {key: value[0] for key, value in parse_qs(urlsplit(url).query).items()}


@get_callback_path
def split_cookies(cookie: str, **kwargs):
    """
    将cookies拆开，便于抓包分析
    Args:
        cookie:

    Returns:

    """
    main_path = kwargs.get('path')
    with open(os.path.join(main_path, 'cookie.txt'), 'a+') as f:
        res = '\n'.join([unquote_plus(x) for x in cookie.split('; ')])
        logger.info(res)
        f.write(res + '\n\n\n\n')


def requests_cookie(cookie: dict):
    """
    requests库cookies分割
    :param cookie:
    :return:
    """
    return '; '.join([f"{key}={value}" for key, value in cookie.items()])


def selenium_cookie(cookie: list):
    """
    转换为浏览器的cookie
    [{'domain': '.51job.com', 'expiry': 1656852518, 'httpOnly': False, 'name': 'ssxmod_itna', 'path': '/', 'secure': False, 'value': 'Qq+xniDQitgDy7DzhmeG=Ar3xfhDGTRqheGQFDlrnoxA5D8D6DQeGTbRK+voI1oDZYP0xFSQBb3iOFhWOepobpBmeDHxY=DU=DPYoD4RKGwD0eG+DD4DWDmnFDnxAQDjxGPc0EHv=DEDYPcDA3Di4D+WwQDmqG0DDt7R4G2D7tcU0meWM0jFCUowkGqoGDcD0U3xBLtW1u5H6ceRM0rdaIsD0P=uaheR=w5Qx0WYqGyQKGufktZ98RCkkNMDleqb2mofRe0S7p4DOxqCYq372ehuUwdjYmP0Yqhji+f3hDDGfmSPD==='}, {'domain': '.51job.com', 'expiry': 1656852518, 'httpOnly': False, 'name': 'ssxmod_itna2', 'path': '/', 'secure': False, 'value': 'Qq+xniDQitgDy7DzhmeG=Ar3xfhDGTRqheGQD6hzriD0v+Ex03YGujeADwpB4jKD2bYD'}, {'domain': '.51job.com', 'expiry': 1641312002.72257, 'httpOnly': True, 'name': 'partner', 'path': '/', 'secure': False, 'value': '51jobhtml5'}, {'domain': '.51job.com', 'expiry': 1643892517.722496, 'httpOnly': True, 'name': 'm_search', 'path': '/', 'secure': False, 'value': 'areacode%3D010000'}, {'domain': '.51job.com', 'expiry': 1704372517.722393, 'httpOnly': True, 'name': 'guid', 'path': '/', 'secure': False, 'value': 'aab74a351f3bddbc5728bcdd9a563a22'}, {'domain': 'msearch.51job.com', 'expiry': 1641302317.721497, 'httpOnly': True, 'name': 'acw_tc', 'path': '/', 'secure': False, 'value': '76b20ffb16413005152697280e022e172e3be2bb9f6b465326b382b15a20ce'}, {'domain': 'msearch.51job.com', 'expiry': 1956660518, 'httpOnly': False, 'name': '_uab_collina', 'path': '/jobs/beijing-xcq', 'secure': False, 'value': '164130051890153957032396'}]

    Returns:

    """
    cookies = []

    for item in cookie:
        lp = f"{item.get('name')}={item.get('value')}"
        cookies.append(lp)

    return '; '.join(cookies)


def dict_sort(data: dict):
    return dict(sorted(data.items(), key=lambda x: x[0]))


def convert_request_headers():
    """
    正则实现
    referer: https://mo.m.taobao.com/union/share_link?spm=a21wq.b1013274.zhuanlian.5&needlogin=1&union_lens=recoveryid%3AYchuxoDi.rgDAK43OrblWFKP_1643345221655_1594351422_21549244%3Bprepvid%3AYchuxoDi.rgDAK43OrblWFKP_1643345415007_5422204_21549244
    x-sgext: JAGTQ2g4OrlMYIyrKQZyV0Oic6JzpWChc6Z1pGCndrBgonWncKB3pnKqdg%3D%3D
    x-sign: az7A0Z003xAAItdhHGUp2SOx4o41stdi0kEoRM5SXgvB80PTSiZkyEappDU%2Bz4sqy%2FFTG%2Bup%2FmKkEBNuh1uTJQVVBvL3Qtdi10LXYt
    Returns:

    """
    # 由该工具提供
    # https://uutool.cn/header2json/


def dict2js_json(body_data):
    """
    将python字典类型进行转换
    Args:
        body_data:

    Returns:

    """
    return json.dumps(body_data, ensure_ascii=False).replace(" ", "")


@get_callback_path
def export_data_by_mongo(db, collection, conn="mongodb://localhost:27017/", **kwargs):
    """
    mongo导出工具方法
    :param db:
    :param collection:
    :param kwargs:
    :return:
    """
    client = pymongo.MongoClient(conn)
    coll = client[db][collection]
    data = (x for x in coll.find())
    df = pd.DataFrame(data)
    df.drop_duplicates(subset='name', inplace=True)
    df = df[['name']]
    main_path = kwargs.get('path')
    df.to_csv(f'{os.path.join(main_path, collection)}.csv', index=False, encoding='utf-8-sig')


def china_code(province=None):
    """
    获取县城信息
    :return:
    """
    file = os.path.join(LIB_PATH, 'resources/china.json')
    with open(file) as f:
        data = json.loads(f.read())
    data = filter(lambda x: x.get('name') == province, data) if province else data
    for area in data:
        yield from area['child']


def image_download(url: str):
    """
    https://ssl-panoimg132.720static.com/resource/prod/64535b4cs92/7c9jO7kveu6/49502875/1647055527/imgs/thumb.jpg
    cors 下载
    :param url:
    :return:
    """
    netloc = split_query_param(url)[0]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36',
        'Origin': netloc,
        'referer': netloc
    }
    return requests.get(url, headers=headers)


def get_b64(image):
    """
    获取文件的base64编码值
    :param image:
    :return:
    """
    with open(image, 'rb') as f:
        image = f.read()
        image_base64 = str(base64.b64encode(image), encoding='utf-8')
    return image_base64


def is_chinese(word):
    """
    判断是否是汉字
    :param word:
    :return:
    """
    wd_lt = []
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            wd_lt.append(True)
        else:
            wd_lt.append(False)
    return all(wd_lt)


def gen_random_nums(num):
    """
    返回随机字符串或者随机数字
    :param num:
    :return:
    """
    data = ''.join([str(random.randint(1, 9)) for _ in range(num)])
    return data


def except_charset_handle(x, printable=False):
    """
    处理windows控制台打印异常
    :param x:
    :param printable:
    :return:
    """
    if printable:
        print(x.encode("gbk", 'ignore').decode("gbk", "ignore"))
    else:
        return x.encode("gbk", 'ignore').decode("gbk", "ignore")


def delete_tab(x: str):
    """
    \r 左换行
    \n 右换行
    \t 四个空格
    :param x:
    :return:
    """
    y = x.replace('\t', '').replace('\n', '').replace('\r', '')
    return except_charset_handle(y)


def today(full=False):
    """
    返回年月日或年月日时分秒
    :param full:
    :return:
    """
    if full:
        rule = '%Y-%m-%d %H:%M:%S'
    else:
        rule = '%Y-%m-%d'
    dt = datetime.now().strftime(rule)
    return dt


def get_local_ip():
    """
    get local ip
    """
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    return ip


def zip_file(dir_path, zip_name):
    """
    压缩文件夹
    https://blog.csdn.net/zichen_ziqi/article/details/119768875
    :param dir_path:
    :param zip_name:
    :return:
    """
    zip_object = zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED)
    for path, _, filenames in os.walk(dir_path):
        # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
        file_path = path.replace(dir_path, '')
        for filename in filenames:
            zip_object.write(os.path.join(path, filename), os.path.join(file_path, filename))
    zip_object.close()
    logger.info("文件夹\"{0}\"已压缩为\"{1}\".".format(dir_path, zip_name))


def unzip_file(file_name, path):
    """
    解压文件
    :param path:
    :param file_name
    :return:
    """
    with zipfile.ZipFile(file_name) as zf:
        zf.extractall(path)


def get_cmd_print(cmd) -> str:
    '''
    执行命令行参数并返回
    :param cmd:
    :return:
    '''
    r = os.popen(cmd)
    text = r.read()
    r.close()
    return delete_tab(text)
