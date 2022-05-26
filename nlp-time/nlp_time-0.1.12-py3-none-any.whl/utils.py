# -*-coding:utf-8-*-
# Author: Eason.Deng
# Github: https://github.com/holbos-deng
# Email: 2292861292@qq.com
# CreateDate: 2022/5/23 14:42
# Description:

def text_pre(text: str):
    text = text.replace("这个月", "本月")
    return text


def around_today(span: int):
    return {2: "前天", 1: "昨天", -1: "明天", -2: "后天"}.get(span, "")
