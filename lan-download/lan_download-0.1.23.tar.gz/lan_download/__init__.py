# encoding=utf-8
import requests
from lxml import etree
from re import findall as re_findall

__version__ = '0.1'
__author__ = "manyouganzhi [https://blog.csdn.net/qq_45429426]"

__save_param = {'save_dir': './'}


def start_download(url=None, show_info=True):
    if type(url) == list:
        for l_url in url:
            download(url=l_url.strip(), show_info=show_info)
        if show_info:
            return print('已完成批量下载')
    elif type(url) == str:
        return download(url=url.strip(), show_info=show_info)
    else:
        return False


# ----------------------------------------------------------------

def start_download_by_password(url: str or list, password: list, show_info=True):
    if type(url) == list:
        if len(url) != len(password):
            return print('带密链接数与密码数不符, 链接数有 {} 个, 密码数有 {} 个.'.format(len(url), len(password)))
        else:
            for goal_url in url:
                for p in password:
                    get_file_url_by_password(url=goal_url, password=p)
    else:
        get_file_url_by_password(url=url, password=password[0])


def get_file_url_by_password(url: str, password: str):

    global content_length
    password_file_html_headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'ccept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': 'codelen=1; pc_ad1=1',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    }

    pw_html_index = requests.get(url=url, headers=password_file_html_headers)
    if pw_html_index.status_code == 200:

        form_sign = re_findall("data : 'action=downprocess&sign=(.*?)&p", pw_html_index.text)[0]
        ajax_pw_file_request_form = {
            'action': 'downprocess',
            'sign': form_sign,
            'p': password
        }
        print(form_sign)

        host_url = 'https://' + url.split('/')[2]

        ajax_pw_file_headers = {
            'accept': 'application/json, text/javascript, */*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-length': str(len(str(ajax_pw_file_request_form))),
            'content-type': 'application/x-www-form-urlencoded',
            'cookie': 'codelen=1; pc_ad1=1',
            'origin': host_url,
            'referer': url,
            'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': "Windows",
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }

        print(ajax_pw_file_request_form)
        print(ajax_pw_file_headers)

        pw_html_index.close()

        ajax_request_by_password = requests.post(url=host_url + '/' + 'ajaxm.php', headers=ajax_pw_file_headers, params=ajax_pw_file_request_form)

        print(ajax_request_by_password.json())

    else:
        return print('无法请求此加密链接，可能链接不存在或网络错误')

# ----------------------------------------------------------------

def download(url, show_info):
    '''
    起始处
    :param show_info: 是否打印关键流程信息
    :param url: 需要下载的链接 str
    :return: 调用解析或者error
    '''
    url_host = 'https://' + url.split('/')[2]  # 解决个性域名的问题
    get_html_text_headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'ccept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': 'codelen=1; pc_ad1=1',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    }
    html = requests.get(url=url, headers=get_html_text_headers)
    if html.status_code == 200:
        # 检测网页请求是否成功
        ajax_headers_info_get(initial_url=url, url_host=url_host, html=html.text, show_info=show_info)
    else:
        return print('无法请求此链接，可能链接不存在或网络错误')


def ajax_headers_info_get(initial_url, url_host, html, show_info):
    '''
    解析关键头信息， /fu?。。。。。
    :param show_info: ...同上
    :param html: 网页源码
    :param initial_url : 原链接
    :param url_host : 链接中的host，解决个性域名问题
    :return: 头信息之一
    '''
    handled_html = etree.HTML(html)
    param_fu_info = handled_html.xpath('/html/body/div[3]/div[2]/div[4]/iframe/@src')[0]  # 获取重要参数
    file_title = handled_html.xpath('/html/body/div[3]/div[1]/text()')[0]  # 获取文件名称，用于最后的保存环节
    ajax_request_url = url_host + param_fu_info  # 构建第一次转折的请求链接
    Qporm = str(param_fu_info).replace('/fu?', '') + ':'
    ajax_form_info_get(initial_url=initial_url, url=ajax_request_url, Qporm=Qporm, title=file_title,
                       show_info=show_info)
    return True


def ajax_form_info_get(initial_url, url, Qporm, title, show_info):
    '''
    接近尾声，获取请求ajax的headers and form     [此模块最近更新于 2022 5]
    :param title: 文件标题
    :param show_info: ...同上
    :param initial_url:初始链接，防止盗链
    :param url:请求链接fu的URL
    :param Qporm:请求时的表单，fu中提取
    :return:ajax headers and form
    '''
    get_ajax_form_headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'ccept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': 'codelen=1; pc_ad1=1',
        'referer': str(initial_url),
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'iframe',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    }
    fu_response_html = requests.get(url=url, headers=get_ajax_form_headers, params=Qporm)
    handled_fu_html = str(fu_response_html.text)
    form_ajaxdata = re_findall("var ajaxdata = (.*?);", handled_fu_html)[0]
    try:
        kernel_form_sign = re_findall(".*?,'sign':'(.*?)','ves':.*?", handled_fu_html)[0]
        kernel_form_ves = re_findall(".*?,'ves':(.*?),'websign':.*?", handled_fu_html)[0]
        kernel_form_websign = str(re_findall(".*?var websign = '(.*?)';\n.*?", handled_fu_html)[0]).strip()
        if kernel_form_websign == '':
            kernel_form_websign = None
        kernel_form_websignkey = re_findall(".*?var websignkey = '(.*?)';\n.*?", handled_fu_html)[0]
    except IndexError:
        kernel_form_sign = re_findall("var ispostdowns = (.*?);", handled_fu_html)[0]
        kernel_form_ves = '1'
        kernel_form_websign = None
        kernel_form_websignkey = 'XoZr'                    # 2022 5

    data = {
        'action': 'downprocess',
        'signs': form_ajaxdata,
        'sign': kernel_form_sign,
        'ves': kernel_form_ves,
        'websign': kernel_form_websign,
        'websignkey': kernel_form_websignkey
    }
    headers_param = ['https://' + initial_url.split('/')[2], url]  # 0--> 头中origin参数 ; 1---> 头中referer参数
    return get_file_url(headers_param=headers_param, data=data, title=title, show_info=show_info)


def get_file_url(headers_param, data, title, show_info):
    '''
    提取文件直链，并专递给下载函数
    :param show_info: ...同上
    :param headers_param: 构建ajax请求头的必要动态参数
    :param data: 请求ajax需要使用的表单数据
    :param title: 第一个函数就已经获取的文件名称，传递给下载函数作为文件名称
    :return: 使用下载函数下载文件
    '''
    ajax_url = headers_param[0] + '/' + 'ajaxm.php'
    ajax_headers = {
        'accept': 'application/json, text/javascript, */*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-length': '152',
        'content-type': 'application/x-www-form-urlencoded',
        'cookie': 'codelen=1; pc_ad1=1',
        'origin': headers_param[0],
        'referer': headers_param[1],
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    file_url_html = requests.post(url=ajax_url, data=data, headers=ajax_headers)
    file_url_html_json = file_url_html.json()
    file_url = str(file_url_html_json["dom"] + '/' + 'file' + '/' + file_url_html_json["url"]).replace(r'\/',
                                                                                                       '/')  # 解析ajax请求返回的json数据，并转为文件的下载直链
    if show_info:
        print(file_url)  # 打印文件直链
    download_file(file_url=file_url, title=title, show_info=show_info)


def download_file(file_url, title, show_info):
    '''
    下载文件的关键函数
    :param show_info: ...同上
    :param file_url: 文件直链
    :param title: 文件名称
    :return: 提醒 某某文件下载完成
    '''

    global __save_param
    save_dir = __save_param.get('save_dir')

    download_file_headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': 'down_ip=1',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    }
    request_file_data = requests.get(url=file_url, headers=download_file_headers)
    file_data = request_file_data.content  # 请求并获取文件二进制数据
    with open(save_dir + title, 'wb') as save_file:
        # 保存文件数据
        save_file.write(file_data)
        save_file.close()
    if show_info:
        return print('{}  文件保存完成'.format(title))
    else:
        return None