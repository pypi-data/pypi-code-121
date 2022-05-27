#!/usr/bin/env python
# coding:utf-8
"""功能简要说明
作者：dengqingyong
邮箱：yu12377@163.com
时间：2018/1/12 下午6:20
"""
import uuid
import time
import random
import string
from typing import Tuple
from xpinyin import Pinyin

from .addressinfo import addr
from .bankinfo import bank_bin_list


def get_random_string(length: int = 32) -> str:
    """获取随机字符串"""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def get_uuid(length: int = 32) -> str:
    _uuid36 = str(uuid.uuid1())
    _uuid32 = _uuid36.replace("-", "")
    if length == 36:
        return _uuid36
    elif length == 32:
        return _uuid32
    else:
        return _uuid32[:length]


def get_pinyin(name: str = "", joint_mark="") -> Tuple[str, str]:
    """获取拼音
    :param name: str, 需要转换拼音的汉字
    :param joint_mark: str, 拼音连接符号
    :return 返回拼音与源汉字的元组
    """
    if not name:
        name = get_name()

    p = Pinyin()
    username = p.get_pinyin(name, joint_mark)
    return username, name


def get_name(gender=""):
    """获取中国人惯用姓名"""
    firstnames = """
        赵钱孙李，周吴郑王。
        冯陈褚卫，蒋沈韩杨。
        朱秦尤许，何吕施张。
        孔曹严华，金魏陶姜。
        戚谢邹喻，柏水窦章。
        云苏潘葛，奚范彭郎。
        鲁韦昌马，苗凤花方。
        俞任袁柳，酆鲍史唐。
        费廉岑薛，雷贺倪汤。
        滕殷罗毕，郝邬安常。
        乐于时傅，皮卞齐康。
        伍余元卜，顾孟平黄。
        和穆萧尹，姚邵湛汪。
        祁毛禹狄，米贝明臧。
        计伏成戴，谈宋茅庞。
        熊纪舒屈，项祝董梁。
        杜阮蓝闵，席季麻强。
        贾路娄危，江童颜郭。
        梅盛林刁，钟徐邱骆。
        高夏蔡田，樊胡凌霍。
        虞万支柯，昝管卢莫。
        经房裘缪，干解应宗。
        丁宣贲邓，郁单杭洪。"""

    firstnames = (
        firstnames.replace("，", "")
        .replace("。", "")
        .replace("\n", "")
        .replace(" ", "")
    )
    firstname = random.choice(firstnames)

    secondname_boy = """
    澄邈、德泽、海超、海阳、海荣、海逸、海昌、瀚钰、瀚文、涵亮、涵煦、涵蓄、涵衍、浩皛、浩波、浩博、浩初、浩宕、浩歌、浩广、浩邈、浩气、
    浩思、浩言、鸿宝、鸿波、鸿博、鸿才、鸿畅、鸿畴、鸿达、鸿德、鸿飞、鸿风、鸿福、鸿光、鸿晖、鸿朗、鸿文、鸿轩、鸿煊、鸿骞、鸿远、鸿云、
    鸿哲、鸿祯、鸿志、鸿卓、嘉澍、光济、澎湃、彭泽、鹏池、鹏海、浦和、浦泽、瑞渊、越泽、博耘、德运、辰宇、辰皓、辰钊、辰铭、辰锟、辰阳、
    辰韦、辰良、辰沛、晨轩、晨涛、晨濡、晨潍、鸿振、吉星、铭晨、起运、运凡、运凯、运鹏、运浩、运诚、运良、运鸿、运锋、运盛、运升、运杰、
    运珧、运骏、运凯、运乾、维运、运晟、运莱、运华、耘豪、星爵、星腾、星睿、星泽、星鹏、星然、震轩、震博、康震、震博、振强、振博、振华、
    振锐、振凯、振海、振国、振平、昂然、昂雄、昂杰、昂熙、昌勋、昌盛、昌淼、昌茂、昌黎、昌燎、昌翰、晨朗、德明、德昌、德曜、范明、飞昂、
    高旻、晗日、昊然、昊天、昊苍、昊英、昊宇、昊嘉、昊明、昊伟、昊硕、昊磊、昊东、鸿晖、鸿朗、华晖、金鹏、晋鹏、敬曦、景明、景天、景浩、
    俊晖、君昊、昆琦、昆鹏、昆纬、昆宇、昆锐、昆卉、昆峰、昆颉、昆谊、昆皓、昆鹏、昆明、昆杰、昆雄、昆纶、鹏涛、鹏煊、曦晨、曦之、新曦、
    旭彬、旭尧、旭鹏、旭东、旭炎、炫明、宣朗、学智、轩昂、彦昌、曜坤、曜栋、曜文、曜曦、曜灿、曜瑞、智伟、智杰、智刚、智阳、昌勋、昌盛、
    昌茂、昌黎、昌燎、昌翰、晨朗、昂然、昂雄、昂杰、昂熙、范明、飞昂、高朗、高旻、德明、德昌、德曜、智伟、智杰、智刚、智阳、瀚彭、旭炎、
    宣朗、学智、昊然、昊天、昊苍、昊英、昊宇、昊嘉、昊明、昊伟、鸿朗、华晖、金鹏、晋鹏、敬曦、景明、景天、景浩、景行、景中、景逸、景彰、
    昆鹏、昆明、昆杰、昆雄、昆纶、鹏涛、鹏煊、景平、俊晖、君昊、昆琦、昆鹏、昆纬、昆宇、昆锐、昆卉、昆峰、昆颉、昆谊、轩昂、彦昌、曜坤、
    曜文、曜曦、曜灿、曜瑞、曦晨、曦之、新曦、鑫鹏、旭彬、旭尧、旭鹏、旭东、浩涆、浩瀚、浩慨、浩阔、鸿熙、鸿羲、鸿禧、鸿信、泽洋、泽雨、
    哲瀚、胤运、佑运、允晨、运恒、运发、云天、耘志、耘涛、振荣、振翱、中震、子辰、晗昱、瀚玥、瀚昂、瀚彭、景行、景中、景逸、景彰、绍晖、
    文景、曦哲、永昌、子昂、智宇、智晖、晗日、晗昱、瀚玥、瀚昂、昊硕、昊磊、昊东、鸿晖、绍晖、文昂、文景、曦哲、永昌、子昂、智宇、智晖、
    浩然、鸿运、辰龙、运珹、振宇、高朗、景平、鑫鹏、昌淼、炫明、昆皓、曜栋、文昂"""

    secondname_grid = """
    恨桃、依秋、依波、香巧、紫萱、涵易、忆之、幻巧、水风、安寒、白亦、惜玉、碧春、怜雪、听南、念蕾、紫夏、凌旋、芷梦、凌寒、梦竹、千凡、
    采波、元冬、思菱、平卉、笑柳、雪卉、南蓉、谷梦、巧兰、绿蝶、飞荷、平安、芷荷、怀瑶、慕易、若芹、紫安、曼冬、寻巧、寄波、尔槐、以旋、
    初夏、依丝、怜南、傲菡、谷蕊、笑槐、飞兰、笑卉、迎荷、元冬、痴安、妙绿、觅雪、寒安、沛凝、白容、乐蓉、映安、依云、映冬、凡雁、梦秋、
    梦凡、秋巧、若云、元容、怀蕾、灵寒、天薇、翠安、乐琴、宛南、怀蕊、白风、访波、亦凝、易绿、夜南、曼凡、亦巧、青易、冰真、白萱、友安、
    海之、小蕊、又琴、天风、若松、盼菡、秋荷、香彤、语梦、惜蕊、迎彤、沛白、雁山、易蓉、雪晴、诗珊、春冬、又绿、冰绿、半梅、笑容、沛凝、
    映秋、盼烟、晓凡、涵雁、问凝、冬萱、晓山、雁蓉、梦蕊、山菡、南莲、飞双、凝丝、思萱、怀梦、雨梅、冷霜、向松、迎丝、迎梅、雅彤、香薇、
    以山、碧萱、寒云、向南、书雁、怀薇、思菱、忆文、翠巧、怀山、若山、向秋、凡白、绮烟、从蕾、天曼、又亦、从安、绮彤、之玉、凡梅、依琴、
    沛槐、又槐、元绿、安珊、夏之、易槐、宛亦、白翠、丹云、问寒、易文、傲易、青旋、思真、雨珍、幻丝、代梅、盼曼、妙之、半双、若翠、初兰、
    惜萍、初之、宛丝、寄南、小萍、静珊、千风、天蓉、雅青、寄文、涵菱、香波、青亦、元菱、翠彤、春海、惜珊、向薇、冬灵、惜芹、凌青、谷芹、
    雁桃、映雁、书兰、盼香、向山、寄风、访烟、绮晴、映之、醉波、幻莲、谷冬、傲柔、寄容、以珊、紫雪、芷容、书琴、寻桃、涵阳、怀寒、易云、
    代秋、惜梦、尔烟、谷槐、怀莲、夜山、芷卉、向彤、新巧、语海、灵珊、凝丹、小蕾、迎夏、慕卉、飞珍、冰夏、亦竹、飞莲、海白、元蝶、春蕾、
    怀绿、尔容、小玉、幼南、凡梦、碧菡、初晴、宛秋、傲旋、新之、凡儿、夏真、静枫、痴柏、恨蕊、乐双、念薇、靖雁、寄松、丹蝶、元瑶、冰蝶、
    念波、迎松、海瑶、乐萱、凌兰、曼岚、若枫、傲薇、凡灵、乐蕊、秋灵、谷槐、觅云、寻春、恨山、从寒、忆香、觅波、静曼、青寒、笑天、涵蕾、
    元柏、代萱、紫真、千青、雪珍、寄琴、绿蕊、醉柳、诗翠、念瑶、孤风、曼彤、怀曼、香巧、采蓝、芷天、尔曼、巧蕊"""

    # 随机获取男名与女名
    grid_name = random.choice(
        secondname_grid.replace("\n", "").replace(" ", "").split("、")
    )
    boy_name = random.choice(
        secondname_boy.replace("\n", "").replace(" ", "").split("、")
    )

    # 将两个字的名字随机转换成双字或单字
    if random.randint(1, 3) == 1:
        grid_name = random.choice(grid_name)
        boy_name = random.choice(boy_name)

    # 男名or女名
    if gender.lower() in ("girl", "woman"):
        secondname = grid_name
    elif gender.lower() in ("boy", "man"):
        secondname = boy_name
    elif isinstance(gender, int):
        if gender % 2 == 0:
            secondname = grid_name
        else:
            secondname = boy_name
    else:
        secondname = random.choice([boy_name, grid_name])

    return "{}{}".format(firstname, secondname)


def check_idcards(idcards):
    """函数功能：
    校验模式：1. 校验中国大陆身份证号码的第18位是否正确；
    计算模式：2. 传入前17位，计算第18位校验码返回；
    返回为空时代码校验不通过；
    返回有值时代码校验通过，或是计算模式；
    """
    check_code = ""
    # 统一转换成字符串类型
    try:
        idcards = str(idcards)
    except TypeError as e:
        pass

    # 判断传入的身份证号码长度，如果为18位时顺便截取校验码
    if len(idcards) == 18:
        check_code = idcards[-1:]
        idcards = idcards[:-1]
    elif len(idcards) == 17:
        pass
    else:
        print("输入的身份证号码【{}】位数有误，必须是18位！".format(idcards))
        return check_code

    # 至此已经被转成17位
    # 十七位数字本体码权重
    weight = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    # 对应校验码字符值
    validate = ["1", "0", "X", "9", "8", "7", "6", "5", "4", "3", "2"]

    _sum = 0
    _mode = 0
    for i in range(0, 17):
        try:
            _sum = _sum + int(idcards[i]) * weight[i]
        except TypeError as e:
            print("输入的身份证号码【{}】前17位必须是数字！".format(idcards))
    _mode = _sum % 11
    # 计算模式
    if check_code == "":
        return validate[_mode]
    # 校验模式——校验通过
    elif check_code == validate[_mode]:
        return check_code
    # 校验模式——校验不通过
    else:
        return ""


def get_idcards(sex=0):
    """获取中国大陆18位身份证号码"""
    # part1: 随机获取地区编码
    area_code = random.choice(addr)[0]

    # part2: 随机获取1949/10/01到当天的一个日期
    # 日期起始时间: 1949/10/01 00:00:00
    start_timestamp = -639129600
    # 日期结束时间：当天
    end_timestamp = round(time.time())
    birthdate_timestamp = random.randrange(start_timestamp, end_timestamp, 86400)
    birthdate = time.strftime("%Y%m%d", time.localtime(birthdate_timestamp))

    # part3: 随机获取两位顺序码
    sequence_code = random.randrange(11, 99)

    # part4：性别编码：奇怪代表男性，偶数代码女性
    if sex == 0:
        sex_code = random.randrange(1, 10)
    elif sex % 2 == 1:
        sex_code = random.randrange(1, 10, 2)
    else:
        sex_code = random.randrange(2, 10, 2)

    # part5: 计算校验码
    check_code = check_idcards(
        "{}{}{}{}".format(area_code, birthdate, sequence_code, sex_code)
    )

    return "{}{}{}{}{}".format(
        area_code, birthdate, sequence_code, sex_code, check_code
    )


def get_mobile_no():
    """生成随机手机号码"""
    phone_head = [
        130,
        131,
        132,
        133,
        134,
        135,
        136,
        137,
        138,
        139,
        150,
        151,
        152,
        155,
        158,
        170,
        171,
        172,
        173,
        174,
        175,
        176,
        177,
        178,
        179,
        181,
        186,
        187,
        188,
        189,
    ]
    phone_no = str(random.choice(phone_head)) + "".join(
        random.choice("0123456789") for i in range(8)
    )
    return phone_no


def get_phone_serial_no():
    """生成手机串号"""
    serial_no = "".join(random.choice(string.ascii_uppercase) for i in range(4))
    serial_no += "-" + "".join(
        random.choice(string.ascii_uppercase) for i in range(4)
    )
    serial_no += "-" + "".join(random.choice(string.digits) for i in range(5))
    return serial_no


def get_bank_no(num=1, bank=None, bank_name=None, ftype=None, length=None, first=None):
    """生成银联卡卡号
    :param bank: 银行简称，大写字母，如工行ICBC，建行CCB，农行ABC等——非必填，默认随机
    :param ftype: 卡片类型，储蓄卡DC，信用卡CC——非必填，默认随机
    :param length: 卡号长度，信用卡基本上都是16位，储蓄卡通常16至19位，最长19位，但偶尔有低有16位的——非必填，默认随机
    :param num: 一次生成的卡号数量——非必填，默认1
    :param first: 为True时返回一个对象，非True时返回列表
    """

    if length and (int(length) < 16 or int(length) > 19):
        raise ValueError("银联卡号通常是16到19数字，请检查输入的length参数")

    # 获取参数获取bin码
    bin_list = get_bank_bin(
        num=num, bank=bank, bank_name=bank_name, ftype=ftype, length=length
    )

    for bin in bin_list:
        __get_bank_no(bin_obj=bin)
    if first:
        return bin_list[0]
    else:
        return bin_list


def __get_bank_no(bin_obj):
    if not bin_obj["bin"].isdigit():
        raise ValueError("银行卡BIN应该为6位数字")

    # 中间数字长度=长度 - 6位bin长度 - 末位校验码
    part2_length = int(bin_obj["length"]) - len(bin_obj["bin"]) - 1
    bank_part2 = ""
    for i in range(part2_length):
        bank_part2 += str(random.randint(0, 9))

    # 计算末尾校验码
    bank_no = bin_obj["bin"] + bank_part2
    fsum = 0
    _index = 0
    while True:
        _index -= 1
        try:
            _value = int(bank_no[_index])
        except IndexError as e:
            break
        # 判断位置
        if abs(_index) % 2 == 1:
            # 倒数：奇数位时*2
            _value *= 2
            if _value >= 10:
                # 十位数时：取个位数字与十位数字相加
                fsum += _value - 9
            else:
                # 个位数时：直接采用
                fsum += _value
        else:
            # 倒数：偶数位时直接相加
            fsum += _value
    # 拼接末尾校验码
    if fsum % 10 == 0:
        check_no = 0
    else:
        check_no = 10 - fsum % 10
    bank_no += str(check_no)
    bin_obj["no"] = bank_no
    return bin_obj


def get_bank_bin(
    num: int = 1,
    bank: str = None,
    bank_name: str = None,
    ftype: str = None,
    length: str = None,
):
    """获取银行卡bin码"""
    if length:
        length = str(length)
    bin_list = []
    # 根据条件过滤
    for _bin in bank_bin_list:
        if bank and _bin["bank"] != bank:
            continue
        if bank_name and not _bin["name"].startswith(bank_name):
            continue
        if ftype and _bin["type"] != ftype:
            continue
        if length and _bin["length"] != length:
            continue
        bin_list.append(_bin)
    if not bin_list:
        if ftype == "CC" and int(length) > 16:
            raise ValueError("找不到对应的bin码，信用卡通常是16位，请检查输入的length参数")
        raise ValueError("找不到对应的bin码，请检查输入是否正确！")
    if num <= 0:
        return bin_list
    else:
        return random.choices(bin_list, k=num)
