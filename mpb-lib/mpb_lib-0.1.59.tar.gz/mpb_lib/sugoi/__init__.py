# sugoiパッケージ用の初期化スクリプト
# 
# Copyright (c) 2021 Atsush Shibata(shivata@m-info.co.jp)
#
# Released under the MIT license.

from datetime import datetime
from json import loads
import requests
from bs4 import BeautifulSoup
import numpy as np


def doomsday_clock(year):
    dc_url = "https://ja.wikipedia.org/wiki/%E4%B8%96%E7%95%8C%E7%B5%82%E6%9C%AB%E6%99%82%E8%A8%88"
    resp = requests.get(dc_url)
    soup = BeautifulSoup(resp.text, 'html.parser')

    secs = {}

    table = [x for x in soup.find_all("table", class_="wikitable")]
    for n, tr in enumerate(table[0].find_all("tr")):
        if n > 1:
            tds = [x for x in tr.find_all("td")]
            mstr = tds[1].text.replace("前", "")
            smstr = mstr.split("分")
            sec = 0
            if smstr[1]:
                sec = int(smstr[0])*60+int(smstr[1].replace("秒", ""))
            else:
                sec = int(smstr[0])*60
            secs[int(tds[0].text.replace("年", ""))] = sec

    if year in secs:
        return secs[year]
    else:
        return "不明"


def get_number_of_space_satellite():
    resp = requests.get("https://www.ucsusa.org/media/11490")
    lines = len(resp.text.split("\n"))-1
    return(lines)


def stock_price_prediction():
    """
    ランダムな[-1, 1]のうちランダムに数値を返す
    """
    return choice([-1, 1])


def get_wf_json(code=13):
    url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{code:02}0000.json"
    resp = requests.get(url)
    d = loads(resp.text)
    return d



def pp(code=13):
    """
    codeにある地域(デフォルトは東京)の
    直近の降水確率を返す
    """
    d = get_wf_json(code)
    return int(d[0]["timeSeries"][1]["areas"][0]["pops"][0])


def temp(code=13):
    """
    codeにある地域(デフォルトは東京)の
    直近の気温予測を返す
    """
    d = get_wf_json(code)
    c = int(d[0]["timeSeries"][2]["areas"][0]["temps"][0])
    return int(1.8*c+32)


def f2c(f):
    """
    華氏(Fahrenheit)から摂氏(Celsius)に変換
    """
    return int((f-32)*(5/9))


def ppl(code=13):
    """
    codeにある地域(デフォルトは東京)の直近の降水確率を返す
    6時間ごと，4つ
    """
    d = get_wf_json(code)
    return [int(x) for x in d[0]["timeSeries"][1]["areas"][0]["pops"]][:4]


coef = np.array([0.02975907, -1.47542641, 19.58163225, 21.7626419])


def test_score(h):
    """
    勉強時間に対する，テストの点数を返す
    100点満点，10時間で限界効用逓減によって下がって行く。
    """
    if h > 20:
        h = 20
    score = int(np.poly1d(coef)(h))+1
    if score > 100:
        score = 100
    return score


def test_score2(h, i):
    if h > 20:
        h = 20
    score = np.poly1d(coef)(h)+1-20
    score = int(score*(i/100)+20)
    if score > 100:
        score = 100
    return score


def get_eq_info():
    dc_url = "https://api.p2pquake.net/v2/jma/quake?limit=1"
    resp = requests.get(dc_url)
    ql = loads(resp.text)
    q = ql[0]
    return q.get("earthquake", {})


def get_eq_info2():
    """
    api.p2pquake.netから，日本で発生した直近の地震の情報を取り出す
    戻り値は辞書
    """
    # 地震の情報を読み込む
    url = "https://api.p2pquake.net/v2/jma/quake?limit=1"
    r = requests.get(url)
    ql = loads(r.text)
    dt = ql[0]["created_at"]
    dto = datetime.strptime(ql[0]["created_at"].split(".")[0], "%Y/%m/%d %H:%M:%S")
    retd = ql[0]["earthquake"]["hypocenter"]
    retd["datetime"] = dto
    return retd


