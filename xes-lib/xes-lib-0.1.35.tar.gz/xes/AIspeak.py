import requests
import time
import pygame
from xes import common

g_gender="male"
g_rate=None
g_pitch=None

#设置语音性别
def setmode(gender):
    if gender == "boy":
        gender = "male"
    elif gender == "girl":
        gender = "female"

    global g_gender
    g_gender = gender


#设置语速
def setspeed(rate):
    if not isinstance(rate, int) and not isinstance(rate, float):
        raise Exception("语速设置功能参数范围为0-2，调整下参数范围吧")

    if rate < 0 or rate > 2:
        raise Exception("语速设置功能参数范围为0-2，调整下参数范围吧")

    global g_rate
    g_rate = rate


#设置音高
def sethigh():
    global g_pitch
    g_pitch = "high"


#文本转语音
def speak(text):
    text = text.strip()
    if text == "":
        raise Exception("文本不能为空")

    print("语言服务正在处理中，请耐心等待...")

    global g_gender,g_rate,g_pitch
    params = {"text":text,"gender":g_gender,"rate":g_rate,"pitch":g_pitch}
    cookies = common.getCookies()
    headers = {"Cookie": cookies}
    rep = requests.get("https://code.xueersi.com/api/ai/python_tts/tts", params=params, headers=headers)
    repDic = common.jsonLoads(rep.text)
    if repDic is None:
        raise Exception("微软语言服务请求超时，请稍后再试")

    if repDic["stat"] != 1:
        raise Exception(repDic["msg"])

    voiceUrl = repDic["data"]["url"]
    duration = repDic["data"]["duration"]

    #下载语音文件
    r = requests.get(voiceUrl)
    filename = voiceUrl.split("/")[-1]
    with open(filename, "wb") as f:
        f.write(r.content)
    f.close()

    #调用pygame播放
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    print("语言服务处理完毕！")

    time.sleep(duration + 1)


#翻译
def translate(text):
    text = text.strip()
    if text == "":
        return ""

    print("语言服务正在处理中，请耐心等待...")

    params = {"text": text}
    cookies = common.getCookies()
    headers = {"Cookie": cookies}
    rep = requests.get("https://code.xueersi.com/api/ai/python_tts/translate", params=params, headers=headers)
    repDic = common.jsonLoads(rep.text)
    if repDic is None:
        raise Exception("微软语言服务请求超时，请稍后再试")

    if repDic["stat"] != 1:
        raise Exception(repDic["msg"])

    print("语言服务处理完毕！")

    result = repDic["data"]["text"]
    return result