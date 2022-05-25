import time
import datetime
import requests
import pygame
from xes import sms, weather
# 获取一个垃圾信息关键字列表
def junk_info():
    return ["保险", "投资", "银行卡", "贷款", "免息", "购车", "置房", "中奖", "中大将", "大将", "免服务费", "免费", "理财产品"]
    pass

# 计算两个日期之间差几天
def date_diff(d1, d2):
    d1 = time.strptime(d1, "%Y-%m-%d")
    d2 = time.strptime(d2, "%Y-%m-%d")
    data1 = datetime.datetime(d1[0], d1[1], d1[2])
    data2 = datetime.datetime(d2[0], d2[1], d2[2])
    da = data1 - data2
    return da.days

# 播放mp3
def play_mp3(music, seconds = None):

    if not isinstance(music, str):
        raise Exception("参数必须为字符串")

    # allMusics = {
    #     "baba.mp3":5,
    #     "lala.mp3":6,
    #     "lulu.mp3":6,
    #     "goodbye.mp3":10,
    #     "oh no.mp3":7,
    #     "try again.mp3":6,
    #     "蔡健雅,MC Hotdog - Easy Come Easy go.mp3":226,
    #     "胡66 - 浪人琵琶.mp3":224
    # }
    # if music not in allMusics.keys():
    #     return "所选音乐不存在，请检查音乐名称拼写是否正确"
    # musicUrl = "https://icourse.xesimg.com/programme/python_music/v20190814/" + music
    #
    # # 下载语音文件
    # r = requests.get(musicUrl)
    # filename = musicUrl.split("/")[-1]
    # with open(filename, "wb") as f:
    #     f.write(r.content)
    # f.close()

    # 调用pygame播放
    pygame.mixer.init()
    pygame.mixer.music.load(music)
    pygame.mixer.music.play()
    if seconds is not None:
        time.sleep(seconds)
        pygame.mixer.music.stop()

    # data = { 'type':'result','desc':'播放音乐','value' : musicUrl }
    # InfoTransferAndExchange(data)

    #播放音乐直到停止，sleep音乐的时长
    #冗余1秒的加载延迟
    # s = allMusics[music] + 1
    # time.sleep(s)
    return ""


def send_msg(mobile, content):
    return sms.send_msg(mobile, content)

def air_temp(location, start = 0):
    return weather.air_temp(location, start)

def air_speed(location, start = 0):
    return weather.air_speed(location, start)

def newprint(words, sleep_time = 0.1):
    for i in words:
        print(i , end = '',flush=True)
        time.sleep(sleep_time)
    print("",end="\n")

def newinput(words, sleep_time = 0.1):
    for i in words:
        print(i , end = '',flush=True)
        time.sleep(sleep_time)
    print("",end="\n")
    i = input()
    return(i)