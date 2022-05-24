# -*- coding: utf-8 -*-

import traceback
import re
from lxml.html import fromstring

# from lxml import etree
from lxml import html as etree
import re
# import HTMLParser
import json
import sys


"""
from lxml import etree
html = etree.HTML(text)
"""

class BaiduExtractor(object):
    """
    百度搜索页面解析器
    示例：
    """

    def __init__(self):
        pass

    def extractor(self, text):
        """
         获取pc排名数据
         response_status 0请求失败 1 请求成功 2 页面不全，封ip
         百度关键词列表页数据
            返回 页面所有内容
            2 ： 页面异常 或 不全百度相关结果数
            0 ：没有数据
            -1 ： 异常
        brand_area   品牌专区  h2 有两个
        brand_website  官网  a 两个 内容 全匹配 官网
        """
        if not isinstance(text, str):
            text = text.decode(encoding="utf-8", errors='ignore') # bytes to str  用于匹配字符串

        if text.find('location.href.replace') >= 0:
            return 2
        elif text.find(u'页面不存在_百度搜索') > -1 or text.find(u'很抱歉，没有找到与') > -1:
            return dict()
        elif text.find(u'id="container"') < 0 or text.find(u'id="content_left"') < 0:
            return 0
        else:
            ext_result = dict()
            baidu_product_cnt = 0
            aladdin_cnt = 0
            ad_cnt = 0
            results_num = 0
            nature_cnt = 0
            include = ''
            try:
                advert = re.findall(r'class="m">广告<', text)
                ad_cnt = len(advert) if advert else 0
                print("广告数: {}".format(ad_cnt))

                # tree = fromstring(text.decode("utf-8", "ignore"))
                tree = fromstring(text)     # py3 自动转换
                containers = tree.cssselect('div.c-container')  # *行代码
                if containers:
                    rank_result_list = list()
                    for container in containers:
                        toprank = 0
                        title = ''
                        des = ''  # 描述
                        evaluate = ""  # 评价
                        realaddress = ""
                        domain = ""
                        show_date = ""
                        special_mark = 0
                        snapshoot_url = ""
                        keep_red = dict()

                        class_name = container.get("class")
                        if class_name.find("result-op") > -1:
                            special_mark = 3

                        toprank = int(container.get('id'))
                        # 标题
                        titles = container.cssselect("h3")
                        if titles:
                            # title = str(self.get_text(titles[0])).encode("utf-8").replace(u"举报图片", "").strip()
                            title = str(self.get_text(titles[0])).replace(u"举报图片", "").strip()
                            keep_red['title'] = re.findall(r'<em>.*?</em>', title)

                            if title.find("官网") > -1:
                                special_mark = 2
                            elif title.find("品牌") > -1:
                                special_mark = 1

                        # 内容
                        des_list = container.cssselect("div.c-abstract")
                        if len(des_list) > 0:
                            # des = self.get_text(des_list[0])
                            des = etree.tostring(des_list[0], encoding="utf-8", method="text").decode(encoding="utf-8")
                            # keep_red['desc'] = re.findall(r'<em>.*?</em>', etree.tostring(des_list[0], encoding="utf-8", method="text")) # py2

                            keep_red['desc'] = re.findall(r'<em>.*?</em>', des)
                            show_date_eles = des_list[0].xpath('descendant::span')
                            if show_date_eles:
                                show_date = etree.tostring(show_date_eles[0], encoding="utf-8", method="text").strip().decode(encoding="utf-8")
                                show_date = str(show_date).split("-")[0].strip().replace(" ", "")

                        else:
                            des_list = container.cssselect("div.c-span18c-span-last")
                            if len(des_list) > 0:
                                des = self.get_text(des_list[0])
                                keep_red['desc'] = re.findall(r'<em>.*?</em>', des)

                                show_date_eles = des_list[0].xpath('descendant::span[@class="m"]')
                                if show_date_eles:
                                    show_date = etree.tostring(show_date_eles[0], encoding="utf-8",
                                                               method="text").strip().decode(encoding="utf-8")
                                    show_date = str(show_date).split("-")[0].strip().replace(" ", "")
                            else:
                                des_list = container.cssselect("div.c-gap-top-small")
                                if des_list:
                                    des = self.get_text(des_list[0])
                                    # keep_red['desc'] = re.findall(r'<em>.*?</em>', etree.tostring(des_list[0]))

                                    keep_red['desc'] = re.findall(r'<em>.*?</em>',
                                                                  etree.tostring(des_list[0], encoding="utf-8",
                                                                    method="text").decode(encoding="utf-8"))
                                    show_date_eles = des_list[0].xpath('descendant::span')
                                    if show_date_eles:
                                        show_date = etree.tostring(show_date_eles[0], encoding="utf-8",
                                                                   method="text").strip().decode(encoding="utf-8")
                                        show_date = str(show_date).split("-")[0].strip().replace(" ", "")

                        realaddress_list = container.cssselect("a")
                        if len(realaddress_list) > 0:
                            realaddress = realaddress_list[0].get("href")
                        # domain 显示url
                        domain_list = container.cssselect("a.c-showurl")
                        if len(domain_list) > 0:
                            # domain = self.get_text(domain_list[0]).strip()
                            # keep_red['url'] = re.findall(r'<b>.*?</b>', etree.tostring(domain_list[0]))   # py2

                            domain = etree.tostring(domain_list[0], encoding="utf-8", method="text").decode(
                                encoding="utf-8")
                            if domain.find("}") > -1:
                                domain = domain.split("}")[1]
                            keep_red['url'] = re.findall(r'<b>.*?</b>', domain)
                        else:
                            domain_list = container.cssselect("span.c-showurl")
                            if len(domain_list) > 0:
                                domain = self.get_text(domain_list[0]).strip()
                                if domain.find("}") > -1:
                                    domain = domain.split("}")[1]
                                keep_red['url'] = re.findall(r'<b>.*?</b>', domain)

                        if domain == "":
                            domain_list = container.cssselect("div.g")
                            if len(domain_list) > 0:
                                domain = self.get_text(domain_list[0]).strip()
                                if domain.find("}") > -1:
                                    domain = domain.split("}")[1]
                                keep_red['url'] = re.findall(r'<b>.*?</b>', domain)
                        if domain == "":
                            domain_list = container.cssselect("span.g")
                            if len(domain_list) > 0:
                                domain = self.get_text(domain_list[0]).strip()
                                if domain.find("}") > -1:
                                    domain = domain.split("}")[1]
                                keep_red['url'] = re.findall(r'<b>.*?</b>', domain)

                        if title.find(u"的最新相关信息") > -1:
                            domain = "baidu"

                        if domain.find(".baidu.") > -1:
                            # baidu_product_cnt += 1
                            special_mark = 4
                        else:
                            nature_cnt += 1

                        if domain.find("image.baidu.") > -1:
                            des = "百度图片"
                        if not des:
                            try:
                                if domain_list:
                                    domain_list[0].getparent().remove(domain_list[0])
                                if titles:
                                    titles[0].getparent().remove(titles[0])
                                des = str(self.get_text(container)).split("查看更多")[0]
                                if domain.find("tieba.baidu.") > -1:
                                    # 百度贴吧
                                    des = des.split("杜绝广告")[1]
                            except:
                                des = ""
                        item = dict()

                        div_html = etree.tostring(container, encoding='utf-8', method='html').decode(encoding="utf-8")
                        if div_html.find('aladdin') > 0 or div_html.find('alading') > 0:
                            item['alading'] = 1
                        else:
                            item['alading'] = 0
                        item['show_url'] = domain
                        item['rank'] = toprank
                        item['show_title'] = title
                        item['show_desc'] = des
                        item['url'] = realaddress
                        item["special_mark"] = special_mark
                        item["show_date"] = show_date
                        # item["snapshoot_url"] = snapshoot_url
                        # if keep_red:
                        #     for k, v in keep_red.items():
                        #         keep_red[k] = [self.html_parser.unescape(i).replace("<em>", "").replace("</em>", "")
                        #                            .replace("<b>", "").replace("</b>", "")
                        #                        for i in list(set(v))]
                        # item["keep_red"] = json.dumps(keep_red)

                        rank_result_list.append(item)
                else:
                    return 0
                # ext_result["nature_cnt"] = len(containers)
                # ext_result["relate_cnt"] = results_num  # 相关搜索数
                # ext_result["ad_cnt"] = ad_cnt
                # ext_result["aladdin_cnt"] = aladdin_cnt
                # ext_result["baidu_product_cnt"] = baidu_product_cnt  # 百度自由产品数
                # ext_result["include"] = include  # 收录数
                # ext_result["data"] = rank_result_list

                # include_else = re.findall(r'找到相关结果约(.*?)个', text)
                # if include_else:
                #     include = include_else[0]

                results = re.findall(r'百度为您找到相关结果约(.*?)个', text)
                if results:
                    include = int(str(results[0]).replace(",", ""))
                    print("百度相关结果数: {}".format(include))

                related_else = tree.xpath('.//div[@id="rs"]//th/a/text()')
                keyword_list = list()
                for keyword in related_else:
                    keyword_list.append({"keyword": str(keyword)})
                    # keyword_list = ','.join(keyword_list)
                return rank_result_list, include, keyword_list
            except Exception:
                print(traceback.format_exc())
                return -1

    def get_text(self, elem):
        rc = []
        for node in elem.itertext():
            rc.append(node.strip())
        return ''.join(rc)

    def remove_characters(self, previou_url):
        if previou_url.startswith("https://"):
            previou_url = previou_url.replace("https://", "")
        if previou_url.startswith("http://"):
            previou_url = previou_url.replace("http://", "")
        if previou_url.endswith("/"):
            previou_url = previou_url[0:len(previou_url) - 1]
        return previou_url

    def remove_special_characters(self, domain):
        domain = domain.replace("<b>", "")
        domain = domain.replace("</b>", "")
        domain = domain.replace("&nbsp", "")
        domain = domain.replace("....", "")
        domain = domain.replace("...", "")
        return domain


if __name__ == '__main__':
    extractor = BaiduExtractor()
    with open("html_py2.txt", 'r', encoding="utf-8") as     f:
        text = f.read()

    # str -> bytes
    text = text.encode(encoding='utf-8')
    extractor_result = extractor.extractor(text)
    # print(extractor_result)
    result, include, keyword_list = extractor_result
    print(result)
    for r in result:
        for k in r:
            print(k, r[k])
        print("-"*20)

    print(include)
    print(keyword_list)
