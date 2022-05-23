# -*-coding:utf-8-*-
# Author: Eason.Deng
# Github: https://github.com/holbos-deng
# Email: 2292861292@qq.com
# CreateDate: 2022/5/23 14:42
# Description:
import re
import jionlp as jio
from datetime import datetime
from nlp_time.pre import text_pre
from dateutil.relativedelta import relativedelta
from typing import Union


def get_time(text: str, tend_future=True):
    time_text, time_tuple = "", ("", "")
    try:
        text = text_pre(text)
        now = datetime.now()
        time_obj = jio.ner.extract_time(text) or {}
        if not time_obj:
            return "", time_tuple
        time_obj = time_obj[0]
        time_text = time_obj.get("text") or ""
        time_dict = time_obj.get("detail") or {}
        time_tuple = time_dict.get("time") or ["", ""]
        if "inf" in time_tuple[0]:
            t1 = None
        else:
            t1 = datetime.strptime(time_tuple[0], time_format)
        if "inf" in time_tuple[1]:
            t2 = None
        else:
            t2 = datetime.strptime(time_tuple[1], time_format)
        if time_dict.get("type", "") == "time_point":
            if re.findall(re_week, text):
                if tend_future:
                    if t1 and t1 < now:
                        t1 = t1 + relativedelta(weeks=1)
                        t2 = t2 + relativedelta(weeks=1)
                else:
                    if t1 and t1 > now:
                        t1 = t1 - relativedelta(weeks=1)
                        t2 = t2 - relativedelta(weeks=1)
        if isinstance(t1, datetime):
            t1 = t1.strftime(time_format)
        if isinstance(t2, datetime):
            t2 = t2.strftime(time_format)
        time_tuple = (t1, t2)
    except ValueError as _:
        pass
    return time_text, time_tuple


def get_text(time: Union[datetime, str, int]):
    now = datetime.now()
    if isinstance(time, str):
        time = datetime.strptime(time, time_format)
    elif isinstance(time, int):
        time = datetime.fromtimestamp(time)
    duration = now - time
    reply = []
    if not duration.days:
        if duration.seconds < 60:
            return f"{duration.seconds}秒前"
        if duration.seconds < 600:
            return f"{int(duration.seconds / 60)}分钟前"
        day_span = now.day - time.day
        if day_span:
            reply.append({2: "前天", 1: "昨天", -1: "明天", -2: "后天"}.get(day_span, ""))
    else:
        if -2 <= duration.days <= 2:
            reply.append({2: "前天", 1: "昨天", -1: "明天", -2: "后天"}.get(duration.days, ""))
        elif time.year != now.year:
            month_year = now.year - time.year
            if month_year:
                _m = {1: "去年", -1: "明年"}
                reply.append(_m.get(month_year, time.year))
            reply.append(f"{time.month}月")
            reply.append(f"{time.day}号")
        else:
            month_span = now.month - time.month
            if month_span:
                _m = {1: "上个", -1: "下个"}
                reply.append(f"{_m.get(month_span, time.month)}月")
            reply.append(f"{time.day}号")
    if 0 <= time.hour < 6:
        reply.append("凌晨")
    elif 6 <= time.hour < 11:
        reply.append("早上")
    elif 11 <= time.hour < 13:
        reply.append("中午")
    elif 13 <= time.hour < 18:
        reply.append("下午")
    elif 18 <= time.hour:
        reply.append("晚上")
    reply.append(f"{time.hour}点")
    if time.minute > 0:
        reply.append(f"{time.minute}分".zfill(3))
    return "".join(reply)


week_day_strs = "一二三四五六日"
re_week = rf"(?:周|星期)([\d{week_day_strs}])"
time_format = "%Y-%m-%d %H:%M:%S"
