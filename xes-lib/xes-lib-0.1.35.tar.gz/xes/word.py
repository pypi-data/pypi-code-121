import random
from pypinyin import pinyin, lazy_pinyin, Style, load_phrases_dict
from xes import data

# 获得一串汉字的拼音，返回List
def pinyin(str, ls = None):
    # return lazy_pinyin(str, style=Style.FIRST_LETTER)
    if len(str) < 1:
        return ""

    #黄澄澄拼音错误，特殊处理
    personalized_dict = {
        '黄澄澄': [['huáng'], ['dēng'], ['dēng']],
        '呷茶': [['xiā'], ['chá']]
    }
    load_phrases_dict(personalized_dict)
    la = lazy_pinyin(str)
    if ls == "list":
        return la
    else:
        if len(str) == 1:
            return la[0]
        else:
            return la

# 获得一串汉字的拼音,返回空格隔开的字符串
def pinyin2(str, ls = None):
    # return lazy_pinyin(str, style=Style.FIRST_LETTER)
    if len(str) < 1:
        return ""

    #黄澄澄拼音错误，特殊处理
    personalized_dict = {
        '黄澄澄': [['huáng'], ['dēng'], ['dēng']],
        '呷茶': [['xiā'], ['chá']]
    }
    load_phrases_dict(personalized_dict)
    la = lazy_pinyin(str)
    if ls == "list":
        return la
    else:
        if len(str) == 1:
            return la[0]
        else:
            return " ".join(la)

# 获得一个汉字的拼音
def pinyin1(str):
    if len(str) < 1:
        return ""
    return lazy_pinyin(str)[0]

# 随机生成一个汉字
def shengpizi():
    return random.choice(data.shengpizi)

# 随机生成一个词
def shengpici():
    return random.choice(data.shengpici)


# 判断是否是成语
def is_idiom(str):
    if str[0] in data.chengyu:
        if str in data.chengyu[str[0]]:
            return "y"
    return "n"


# 成语接龙
def idiom(str = None):
    if str:
        if str[-1] in data.chengyu:
            return random.choice(data.chengyu[str[-1]])
        else:
            return "n"
    else:
        return random.choice(data.chengyu_base)