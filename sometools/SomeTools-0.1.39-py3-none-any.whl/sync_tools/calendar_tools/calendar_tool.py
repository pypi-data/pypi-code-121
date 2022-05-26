import re
import time
import json
import requests
import datetime
from sometools.sync_tools.base import Base

global calendar_hashmap
calendar_hashmap = dict()


class CalendarMixIn(Base):

    def __init__(self, *args, **kwargs):
        super(CalendarMixIn, self).__init__(*args, **kwargs)

    @staticmethod
    def get_calendar_hashmap() -> dict:
        """
        :return:<class 'dict'>:
        {
            'all_date': ['2022-04-25', '2022-04-26', '2022-04-27', '2022-04-28', '2022-04-29', '2022-04-30', '2022-05-01', '2022-05-02', '2022-05-03', '2022-05-04', '2022-05-05', '2022-05-06', '2022-05-07', '2022-05-08', '2022-05-09', '2022-05-10', '2022-05-11', '2022-05-12', '2022-05-13', '2022-05-14', '2022-05-15', '2022-05-16', '2022-05-17', '2022-05-18', '2022-05-19', '2022-05-20', '2022-05-21', '2022-05-22', '2022-05-23', '2022-05-24', '2022-05-25', '2022-05-26', '2022-05-27', '2022-05-28', '2022-05-29', '2022-05-30', '2022-05-31', '2022-06-01', '2022-06-02', '2022-06-03', '2022-06-04', '2022-06-05'],
            0: ['2022-04-25', '2022-04-26', '2022-04-27', '2022-04-28', '2022-04-29', '2022-05-05', '2022-05-06', '2022-05-09', '2022-05-10', '2022-05-11', '2022-05-12', '2022-05-13', '2022-05-16', '2022-05-17', '2022-05-18', '2022-05-19', '2022-05-20', '2022-05-23', '2022-05-24', '2022-05-25', '2022-05-26', '2022-05-27', '2022-05-30', '2022-05-31', '2022-06-01', '2022-06-02'],
            94: ['2022-04-30', '2022-05-04'],
            92: ['2022-05-01', '2022-05-02', '2022-05-03'],
            90: ['2022-05-07'],
            7: ['2022-05-08', '2022-05-15', '2022-05-22', '2022-05-29'],
            6: ['2022-05-14', '2022-05-21', '2022-05-28'],
            91: ['2022-06-03', '2022-06-04', '2022-06-05']
        }
        all_date: 可判断的日期(Judgable date)
        92/94/91/92 假期(holiday)
        6/7 周末(weekend)
        90 调休工作日(extra working day)
        0 工作日(working day)
        """
        global calendar_hashmap
        now_datetime = datetime.datetime.now()
        now_year = now_datetime.year
        now_month = now_datetime.month if now_datetime.month > 9 else "0" + str(now_datetime.month)
        url = f"https://www.rili.com.cn/rili/json/pc_wnl/{now_year}/{now_month}.js?_={int(time.time() * 1000)}"
        headers = {
            "Host": "www.rili.com.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0",
            "Accept": "text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01",
            "Accept-Language": "en-US,zh-CN;q=0.8,zh;q=0.7,zh-TW;q=0.5,zh-HK;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.rili.com.cn/wannianli/",
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache"
        }
        if calendar_hashmap and calendar_hashmap.get('all_date'):
            if now_datetime.strftime("%Y-%m-%d") not in calendar_hashmap.get('all_date'):
                calendar_hashmap = dict()
        if not calendar_hashmap:
            res = requests.get(url, headers=headers, timeout=30)
            pattern = re.compile('jsonrun_PcWnl\((.*|\n*),"js"\);', flags=re.S)
            match = json.loads(pattern.findall(res.text)[0]).get('data')
            for i in match:  # <class 'dict'>: {'yuethis': -1, 'nian': 2022, 'yue': 4, 'ri': 25, 'r2': '廿五', 'jia': 0, 'jie': '', 'yi': ['祭祀', '祈福', '开光', '解除', '动土', '纳财', '交易', '纳畜', '扫舍'], 'ji': ['进人口', '出行', '结婚', '置产', '安床', '赴任', '安葬', '作灶'], 'jieri': '<a href="/jieridaquan/79744.html" class="jr Yx0">儿童预防接种宣传日</a>,<a href="/jieridaquan/71806.html" class="jr Yx0">世界防治疟疾日</a>', 'shengxiao': '虎', 'jieqi': '谷雨', 'yuexiang': '有明月', 'yuexiang_pinyin': 'youmingyue', 'xingxiu': '西方毕月乌-吉', 'gz_nian': '壬寅', 'gz_yue': '甲辰', 'gz_ri': '戊申', 'wx_nian': '金箔金', 'wx_yue': '覆灯火', 'wx_ri': '大驿土', 'n_yueri': '三月廿五', 'jieqi_link': '<a href="/guyu/" class="jq Yx8">谷雨</a>', 'jieqi_pass': 6, 'jieqi_next_link': '<a href="/24jieqi/lixia/" class="jq Yx8">立夏</a>', 'jieqi_next': 10, 'xingzuo_link': '<a href="/xingzuo/jinniu/" class="xz Yx0">金牛座</a>', 'xingzuo_pinyin': 'jinniuzuo', 'jj_index': 0, 'jj_key': '春', 'jj_pass': 81, 'jj_next': 10, 'week': 1, 'ddd': '周一', 'dddd': '星期一', 'zhouindex': 1}
                if 'all_date' not in calendar_hashmap:
                    calendar_hashmap['all_date'] = []
                calendar_hashmap['all_date'].append(
                    f"{i.get('nian')}-{i.get('yue') if i.get('yue') > 9 else '0' + str(i.get('yue'))}-{i.get('ri') if i.get('ri') > 9 else '0' + str(i.get('ri'))}")
                if i.get('jia') not in calendar_hashmap:
                    calendar_hashmap[i.get('jia')] = []
                calendar_hashmap[i.get('jia')].append(
                    f"{i.get('nian')}-{i.get('yue') if i.get('yue') > 9 else '0' + str(i.get('yue'))}-{i.get('ri') if i.get('ri') > 9 else '0' + str(i.get('ri'))}")
        return calendar_hashmap
