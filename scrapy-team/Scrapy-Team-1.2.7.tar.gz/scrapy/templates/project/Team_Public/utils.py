import json
from datetime import datetime
import re
import pypinyin
import pymongo
import random
import fitz
import requests
import oss2
import hashlib
from scrapy.utils.python import to_bytes
import base64
import json
import requests


def base64_api(url, uname, pwd, img_bin, typeid):
    """   
    typeid:
    一、图片文字类型(默认 3 数英混合)：
    1 : 纯数字
    1001：纯数字2
    2 : 纯英文
    1002：纯英文2
    3 : 数英混合
    1003：数英混合2
     4 : 闪动GIF
    7 : 无感学习(独家)
    11 : 计算题
    1005:  快速计算题
    16 : 汉字
    32 : 通用文字识别(证件、单据)
    66:  问答题
    49 :recaptcha图片识别
    二、图片旋转角度类型：
    29 :  旋转类型
    三、图片坐标点选类型：
    19 :  1个坐标
    20 :  3个坐标
    21 :  3 ~ 5个坐标
    22 :  5 ~ 8个坐标
    27 :  1 ~ 4个坐标
    48 : 轨迹类型
    四、缺口识别
    18 : 缺口识别（需要2张图 一张目标图一张缺口图）
    33 : 单缺口识别（返回X轴坐标 只需要1张图）
    五、拼图识别
    53：拼图识别
"""
    # with open(img, 'rb') as f:
    #     base64_data = base64.b64encode(f.read())
    #     b64 = base64_data.decode()
    base64_data = base64.b64encode(img_bin)
    b64 = base64_data.decode()
    data = {"username": uname, "password": pwd, "typeid": typeid, "image": b64}
    result = json.loads(requests.post(url, json=data).text)
    if result['success']:
        return result["data"]["result"]
    else:
        print(result["message"])

from scrapy.utils.conf import get_config
from scrapy.exceptions import NotConfigured
def upload_local_pdf(path,aim_file_path): 
    if not get_config().get(section="oss_cfg",option="OSS_USER" ):# 提醒设置参数以及设置默认值
        raise NotConfigured("At scrapy.cfg missing 'OSS_USER'")
    if not get_config().get(section="oss_cfg",option="OSS_PASSWORD" ):
        raise NotConfigured("At scrapy.cfg missing 'OSS_PASSWORD'")
    if not get_config().get(section="oss_cfg",option="FILES_STORE" ):
        raise NotConfigured("At scrapy.cfg missing 'FILES_STORE'")
    OSS_USER = get_config().get(section="oss_cfg",option="OSS_USER" )
    OSS_PASSWORD = get_config().get(section="oss_cfg",option="OSS_PASSWORD" )
    auth = oss2.Auth(OSS_USER, OSS_PASSWORD)
    bucket = oss2.Bucket(auth, 'oss-cn-shenzhen.aliyuncs.com', 'xcc2', enable_crc=False)
    file_store = get_config().get(section="oss_cfg",option="FILES_STORE" )
    media_guid = hashlib.sha1(to_bytes(path)).hexdigest()
    new_url = '{}/{}/{}.{}'.format(file_store, aim_file_path, media_guid, 'pdf')
    try:
        with open(path, 'rb') as f:
            # f.seek(0, os.SEEK_SET)
            # current = f.tell()
            bucket.put_object('{}/{}.{}'.format(aim_file_path, media_guid, 'pdf'), f)
    except:
        new_url = ''
    return new_url


def save_img(url, name):
    resp = requests.get(url)
    path = 'Material\imgs' + name
    with open(path, 'wb') as f:
        f.write(resp.content)
    return path


def img_to_pdf(img_path, img_type):
    # file_name = os.path.basename(img_path).replace(img_type, 'pdf')
    file_name = img_path.replace(img_type, 'pdf')
    doc = fitz.open()
    imgdoc = fitz.open(img_path)
    pdfbytes = imgdoc.convertToPDF()
    imgpdf = fitz.open("pdf", pdfbytes)
    doc.insertPDF(imgpdf)
    doc.save(file_name) 
    doc.close()
    return file_name


def parse_ofps(ofps, ofps_):
    # baike key特征
    overviews_ = ['概述', '产品介绍', 'overview', 'overviews']
    features_ = ['特点', '特性', '产品特点', 'feature', 'features']
    applications_ = ['应用', '用途', '应用场景', 'application', 'applications']
    if ofps:
        overviews = []
        features = []
        applications = []
        fps = [re.sub(r'\r|\t|\n|\s+', ' ', fp.strip()) for fp in ofps if fp.strip()]
        fps = [fp.strip().strip('*').strip('◆').strip('·').strip('●').strip('•').strip('■').strip(':').strip('').strip('★').strip('Ø').strip() for fp in ofps if fp]
        fps = [fp for fp in fps if fp]
        on = False
        fn = False
        an = False
        ind0 = 0
        ind1 = 0
        ind2 = 0
        ind3 = 0
        ind4 = 0
        ind5 = 0
        for i, fp in enumerate(fps, start=1):
            fp_ = re.sub(r'\r|\t|\n|\s+', '', fp.lower().strip())
            if (not overviews) and any([True if f == fp_  else False for f in overviews_]):
                ind0 = i
            if (not on) and any([True if f == fp_ else False for f in features_]):
                on = True
                ind1 = i
            if (not features) and any([True if f == fp_ else False for f in features_]):
                ind2 = i
            if (not fn) and any([True if f == fp_ else False for f in applications_]):
                fn = True
                ind3 = i
            if (not applications) and any([True if f == fp_ else False for f in applications_]):
                ind4 = i
            if (not an) and any([True if f == fp_ else False for f in ofps_]):
                an = True
                ind5 = i
        inds1 = [ind for ind in [ind1, ind3, ind5] if ind > 0]
        ind1 = min(inds1) if inds1 else 0
        inds3 = [ind for ind in [ind3, ind5] if ind > 0]
        ind3 = min(inds3) if inds3 else 0
        overviews = fps[ind0:ind1-1] if ind0 and ind1 else fps[ind0:] if ind0 and (not ind1) else fps
        features = fps[ind2:ind3-1] if ind2 and ind3 else fps[ind2:] if ind2 and (not ind3) else []
        applications = fps[ind4:ind5-1] if ind4 and ind5 else fps[ind4:] if ind4 and (not ind5) else []
        overview = '<br>'.join(overviews) if overviews else ''
        feature = '<br>'.join(features) if features else ''
        application = '<br>'.join(applications) if applications else ''
    else:
        overview = ''
        feature = ''
        application = ''
    return overview, feature, application


def parse_list_json_value(host, tr, rowspan_lists, tr_ind, ut=0):
    # ut: 0-text  1-href  2-text|||href
    values = []
    tds = tr.xpath('./*')
    for td in tds:
        href_x = td.xpath('.//a/@href | .//button/@onclick').extract_first()
        href_r = re.search(r'\"(.*)\"', href_x) if href_x else ''
        href = href_r.group(1) if href_r else href_x.strip() if href_x else ''
        src = td.xpath('.//img/@src').extract_first()
        td_rowspan = td.xpath('./@rowspan').extract_first()
        if href and ('javascript' not in href) and (not src):
            url = href if re.search(r'http', href) else host + href.strip('..')
            text = ' '.join([re.sub(r'\r|\t|\n|\s+', ' ', t) for t in deal_list_space(td.xpath('.//text()').extract()) if t])
            if ut == 2:
                val = (text + '|||' + url)
            elif ut == 1:
                val = url
            else:
                val = text
        elif src:
            val = src if re.search(r'http', src) else host + src.strip('..')
        else:
            val = ' '.join([re.sub(r'\r|\t|\n|\s+', ' ', t) for t in deal_list_space(td.xpath('.//text()').extract()) if t])
            # if td_rowspan:
            #     val = ''.join([t.replace('<br>', ' ') for t in deal_list_space(td.xpath('.//text()').extract())])
            # else:
            #     val = '|'.join([t.replace('<br>', ' ') for t in deal_list_space(td.xpath('.//text()').extract())])
            from Team_Public.configs import REP_VUL
            if val in REP_VUL:
                val = ''
        values.append(val)
        if td_rowspan:
            td_ind = tds.index(td)
            num = int(td_rowspan)
            rowspan_lists.append((tr_ind, td_ind, num, val))
    for rowspan_tuple in rowspan_lists:
        raw_tr_ind = rowspan_tuple[0]
        raw_td_ind = rowspan_tuple[1]
        num = rowspan_tuple[2]
        val = rowspan_tuple[3]
        if raw_tr_ind < tr_ind < num + raw_tr_ind:
            values.insert(raw_td_ind, val)
            # if raw_td_ind == 0:
            #     values.insert(0, val)
            # else:
            #     values.insert(raw_td_ind - 1, val)
    return values


def parse_list_json_key(td_reg, text_reg, tr1, tr2=None, key2=None):
    """" 解析list_json key """
    key1 = []
    key2 = [] if not key2 else key2
    # tr1 = table.xpath('./tr[1]')
    # tr2 = table.xpath('./tr[2]')
    tds1 = tr1.xpath(td_reg)
    tds2 = tr2.xpath(td_reg) if tr2 else []
    for td1 in tds1:
        src = td1.xpath('.//img/@src').extract_first()
        if src:
            td_text = src
        else:
            try:
                td_text = td1.xpath(text_reg).extract()
            except:
                td_text = []
            if not td_text:
                try:
                    text_reg = text_reg[:text_reg.rfind('/')]
                    td_text = td1.xpath(text_reg).extract()
                except:
                    td_text = []
            td_text = ' '.join(deal_list_space(td_text))
            # td_text = re.sub(r'\r|\t|\n|((?!<small[^>]*>).)+|((?!<sup[^>]*>).)+|((?!<sub[^>]*>).)+', '', td_text) if td_text else ''
            td_text = re.sub(r'\r|\t|\n|\s+|<(?!(small|/small|sub|/sub|sup|/sup))[^>]*>', ' ', td_text) if td_text else ''
        td_text = td_text.strip()
        col_span = td1.xpath('./@colspan').extract_first()
        row_span = td1.xpath('./@rowspan').extract_first()
        if col_span and int(col_span) > 1:
            key1.append([td_text] * int(col_span))
        elif not row_span or int(row_span) < 2:
            key1.append([td_text])
        else:
            key1.append(td_text)
    for td2 in tds2:
        try:
            td_text = td2.xpath(text_reg).extract()
        except:
            td_text = []
        if not td_text:
            try:
                text_reg = text_reg[:text_reg.rfind('/')]
                td_text = td2.xpath(text_reg).extract()
            except:
                td_text = []
        td_text = ' '.join(deal_list_space(td_text))
        # td_text = td2.xpath(text_reg).xpath('string(.)').extract_first()
        td_text = re.sub(r'\r|\t|\n|\s+|<(?!(small|/small|sub|/sub|sup|/sup))[^>]*>', ' ', td_text) if td_text else ''
        td_text = td_text.strip()
        key2.append(td_text)
    for i, k1 in enumerate(key1):
        ind = i
        if isinstance(k1, list):
            k2 = key2[:len(k1)]
            ks = lists_add((k1, k2))
            key1[ind] = ks
            key2 = key2[len(k2):]
            # for i in range(len(k2)+1):
            #     key2.pop(i)
    keys = []
    for key in key1:
        if isinstance(key, list):
            for k in key:
                keys.append(k)
        else:
            keys.append(key)
    return keys


def parse_list_json_keys(tbody, keys_rowspan, tds_reg, key_text_reg, k):
    if keys_rowspan in [1]:
        k_tds = tbody.xpath('./tr[{}]'.format(keys_rowspan + k)).xpath(tds_reg)
        keys = []
        for k_td in k_tds:
            # text = k_td.xpath(key_text_reg).xpath('string(.)').extract_first()
            try:
                text = k_td.xpath(key_text_reg).extract()
            except:
                text = []
                print(k_td, key_text_reg)
            if not text:
                try:
                    key_text_reg = key_text_reg[:key_text_reg.rfind('/')]
                    text = k_td.xpath(key_text_reg).extract()
                except:
                    text = []
            # td_text = ' '.join(deal_list_space(text))
            td_text = [t.strip() for t in text]
            td_text = ' '.join([tt for tt in td_text if tt])
            # key = re.sub(r'\r|\t|\n|<br[^>]*>|<p[^>]*>|</p>', ' ', td_text) if td_text else ''
            # key = re.sub(r'<(?!(small|/small|sub|/sub|sup|/sup))[^>]*>', '', key) if key else ''
            key = re.sub(r'\r|\t|\n|\s+|<(?!(small|/small|sub|/sub|sup|/sup))[^>]*>', ' ', td_text) if td_text else ''
            keys.append(key.strip())
        # tr1 = tbody.xpath('./tr[{}]'.format(keys_rowspan + k))
        # keys = parse_list_json_key(tds_reg, key_text_reg, tr1)
    elif keys_rowspan in [2]:
        tr1 = tbody.xpath('./tr[{}]'.format(keys_rowspan - 1 + k))
        tr2 = tbody.xpath('./tr[{}]'.format(keys_rowspan + k))
        keys = parse_list_json_key(tds_reg, key_text_reg, tr1, tr2)
    else:
        tr1 = tbody.xpath('./tr[{}]'.format(keys_rowspan + k))
        tr2 = tbody.xpath('./tr[{}]'.format(keys_rowspan - 1 + k))
        keys = parse_list_json_key(tds_reg, key_text_reg, tr1, tr2)
        for kr in range(keys_rowspan - 2, 0, -1):
            tr1 = tbody.xpath('./tr[{}]'.format(kr + k))
            keys = parse_list_json_key(tds_reg, key_text_reg, tr1, None, keys)
    return keys


def category_item(response, config, item, category, level=None, p_category_name=None, p_category_id=None):
    if level:
        item['level'] = level
    if p_category_name: item['p_category_name'] = p_category_name
    if p_category_id: item['p_category_id'] = p_category_id
    # category_name = p_category_name + '_' + category if p_category_name else category
    category_name = category
    category_id = pinyin(category_name, config)
    item['category_name'] = category_name
    item['category_id'] = category_id
    item['url'] = response.url
    item = item_constant(item, config)
    return item


def item_constant(item, config):
    # item["table"] = config.TABLE
    # item["sources"] = config.SOURCES
    # item["creator"] = config.CREATOR
    # item["create_time"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # item['brand_name'] = config.BRAND_NAME
    # item['brand_id'] = config.BRAND_ID
    item["sources"] = config.get('sources')
    item["creator"] = config.get('creator')
    item["create_time"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    item['brand_name'] = config.get('brand_name')
    item['brand_id'] = config.get('brand_id')
    return item


# def up_config(config, brand_name, brand_id, creator, keys, vals, categorys):
#     config.SOURCES = 'manufacturers'
#     config.BRAND_NAME = brand_name
#     config.BRAND_ID = brand_id
#     config.CREATOR = creator
#     #  过滤list_json字段
#     config.DEL_KEY = keys
#     config.DEL_VUL = vals
#     # category过滤
#     config.categorys_names = categorys
#     return config



def mongodb_find_max_date(table_name, filte_dict, sort_str):
    mongocli = pymongo.MongoClient('10.8.108.201', 27018)
    db = mongocli.spider
    db.authenticate("spider", "Dashuju.spider")
    dbcol = db[table_name]
    max_date = ''
    for x in dbcol.find(filte_dict, {sort_str: 1}).sort([(sort_str, -1)]).skip(0).limit(1):
        res = x.get(sort_str)
        if res:
            max_date = res
            break
    return max_date


def lists_add(lists):
    """ 多list相加 """
    results = []
    for tr_text in zip(*lists):
        k = ''
        for tr in tr_text:
            if str(tr) != k.strip():
                k += ' ' + str(tr)
        results.append(k.strip())
    return results


def filter_dict(dicts, config):
    """ 删除dict指定key与value """
    del_key = [k for k in config.get('del_key')]
    del_val = [v for v in config.get('del_val')]
    vals = list(dicts.values())
    keys = list(dicts.keys())
    # key_lower = [k.lower() for k in list(dicts.keys())]
    for i in range(len(vals)):
        if vals[i] in del_val:
            if keys[i] not in del_key:
                del_key.append(keys[i])
    for kk in del_key:
        for key in keys:
            # if kk.lower() in key.lower():
            if kk.lower() == key.lower():
                try:
                    dicts.pop(key)
                    break
                except:
                    continue
    return dicts


def pinyin(word, config):
    """ 汉字转拼音 """
    if (not config.get('brand_name')) or not word: return ''
    result = ''
    for i in pypinyin.pinyin(config.get('brand_name') + '_' + word, style=pypinyin.NORMAL):
        result += ''.join(i)
    return result


def deal_space(lists):
    """ 列表空格删除处理 """
    list_new = []
    for li in lists:
        li_new = re.sub(r'\s|\t|\n', '', li)
        if li_new:
            list_new.append(li_new)
    return list_new


def deal_lines(response, xpath_reg, i):
    res_list = []
    while True:
        results = response.xpath(xpath_reg.format(i)).extract()
        results = deal_space(results)
        if not results:
            break
        res_list += results
        i += 1
    data_list = []
    for res in res_list:
        data_list.append('<p>{}</p>'.format(res))
    return ''.join(data_list)


def deal_list_space(lists):
    """ 列表元素前后空格删除 """
    list_new = []
    for li in lists:
        li = li.strip()
        if li:
            list_new.append(li)
    return list_new


def deal_list_tag(lists, reg=None):
    """ 去除列表元素标签 """
    list_new = []
    for li in lists:
        new_val = re.search(reg, li)
        if new_val:
            list_new.append(new_val.group(1).strip())
    return list_new


def json_dump(item, file):
    datas = json.dumps(dict(item), indent=2, separators=(',', ':'), ensure_ascii=False)
    with open(file, 'a+', encoding='utf-8') as f:
        f.write(datas + '\n')
