# ecoding=utf-8

"""
这是Fishconsole Project最基本的输入输出模块，他起一个辅助控制台输出的作用，当然现在辅助的东西更多了

----

"""

import datetime
import sys

from Fishconsole import fcv

模块开始 = datetime.datetime.now()


def 颜色(text, 色选="None"):
    """
    FishConsole LOGS颜色模块

    ----

    - 将文字按照某种格式格式化然后返回回来

    - 所有的上色都会调用它，所以基本上你不会用到这个东西

    :param text: 你要进行加密的原始文字
    :param 色选: 你要加的颜色，现在的可选颜色是：紫色，红色，黄色，蓝色，青色，绿色和相对应的背景色
    :return: 格式化后的内容
    """
    if 色选 == "紫色":
        return f"\033[35m{text}\033[0m"
    elif 色选 == "红色":
        return f"\033[31m{text}\033[0m"
    elif 色选 == "黄色":
        return f"\033[33m{text}\033[0m"
    elif 色选 == "蓝色":
        return f"\033[34m{text}\033[0m"
    elif 色选 == "青色":
        return f"\033[36m{text}\033[0m"
    elif 色选 == "绿色":
        return f"\033[32m{text}\033[0m"
    elif 色选 == "红背":
        return f'\033[41m{text}\033[0m'
    elif 色选 == "黄背":
        return f'\033[43m{text}\033[0m'
    elif 色选 == "蓝背":
        return f'\033[44m{text}\033[0m'
    elif 色选 == "绿背":
        return f'\033[42m{text}\033[0m'
    elif 色选 == "紫背":
        return f'\033[45m{text}\033[0m'
    elif 色选 == "青背":
        return f'\033[46m{text}\033[0m'
    else:
        return f"{text}"


# 必须使用return的方式输出，其他的方法输出染色将失去效果
# 我也不知道这是为什么，但是它就是这样，我靠，麻了
def 输入(text, 色选="红色"):
    """
    FishConsole LOGS输入模块

    ----

    将文字按照某种格式格式化然后返回回来

    :param text: 显示的文字
    :param 色选: 为指定的内容上色
    :return: 用户输入的值
    """
    res = input(f"{颜色('O', f'{色选}')} 》{text}  {颜色('||》', 色选)}")
    return res


def 日志(text, 色选="Nona"):
    """
    FishConosle LOGS日志模块

    ----

    - 这个嘛，0.0.1时就有了，当时整个模块就三个，split，乱七糟八奇奇怪怪的color还有的就是这个

    - 不得不说，它创建好了就没改过哈哈

    - 其实就是一装逼的，不过为了和普通的print区分开来我在前面加了一个时间戳，它真正有用的是色选参数，嗯，现在优化好了，哎。。现在看到这个真的是感慨啊



    :param text: 你输入的文字
    :param 色选: 上色，具体看FishConsole LOGS颜色模块
    :return: 返回文字，你需要用print输出
    """
    if 色选 != "Nona":
        import time
        return 颜色(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + str(f":{text}"), 色选=色选)
    else:
        import time
        return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + str(f":{text}")


# 先导入参数，一个是updata的参数FI

FI = fcv.f_debug()
FI = FI["Fl"]


# 新建这个函数，默认情况下所有的项目都不会运行，通过传递的参数开启相应的功能（其实都一样）
def 系统日志(text, 参数=False):
    """
    FishConsole LOGS系统日志模块

    ----

    这个跟你没啥关系，由开发者选项决定是否启动


    :param text: 需要显示的文字
    :param 参数: 特定模块的代号
    :return: 指定的文字
    """
    if FI:
        import time
        # 我想精简这个东西，就是用逻辑表达式，如果其中一个条件满足，那就开启这个，但是它只开启一次，下一个使用这个东西传递的参数和自己的参数不一样的话就不开
        # 现在我要的是默认输出，遇到情况就来个无效语句
        if 参数:
            # 这是True时执行的，默认情况下不会执行，但是这里会有一个地方需要注意一下，因为
            # 参数被改了，所以当参数没有被再次更改为False之前其中的任何跟系统日志有关的内容就不会被输出
            # 这个。。虽然能跑了，但是好像实现了又好像没实现。。哎。。开摆
            1 + 1
        else:
            a = 颜色(f"Fishconsole{fcv.version()}" + "》" + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())),
                   色选="紫色") + str(f":{text}")
            print(a)


def 分割线(标题, text, 色选="Nona"):
    """
    FishConsole LOGS分割线模块

    ----

    这个东西的用处就是在控制台上画出一条分割线，让显示的内容更加直观醒目，它支持批量的添加颜色，这样条理更加清楚

    :param 标题: 显示的第一个文本框
    :param text: 显示的第二个文本框
    :param 色选: 设置颜色（具体参考FishcConsole LOGS颜色模块）
    :return:
    """
    if 色选 != "Nona":
        import time
        return "\n\n\n\n\n\n" + 颜色(f"- {标题} -", 色选=色选) + f"  {text}:\n--------------------------\n"
    else:
        return f"\n\n\n\n\n\n- {标题} -  {text}:\n--------------------------\n"


def 变量查看(变量名: str, 变量, 色选: str = "红色"):
    """
    FishCosnole LOGS 变量查看模块

    ----

    - 这个东西的用处就是查看指定变量的数据和类型，并返回这条代码所处的位置


    - 因为个人技术不行，所以你要指定给你看的变量名和给程序看的变量名（如果你知道这个东西的解决办法请务必告诉我(获取变量的变量名)2645602049@qq.com，我在这个模块下面写你的名字/qAq）

    :param 变量名: 给你看的变量名
    :param 变量: 给模块看的变量名
    :param 色选: 上色，具体请看FishConsole LOGS颜色模块
    :return: 经过某种方法格式化后的文字
    """
    行位置 = sys._getframe(1).f_lineno
    type值 = str(type(变量))
    变量类型 = type值.split("'")[1]

    计数器a = 0
    for _ in 变量类型:
        计数器a = 计数器a + 1
    计数器a = 计数器a * 1.4
    计数器a = str(计数器a)
    计数器a = 计数器a.split(".")[0]
    计数器a = int(计数器a)

    计数器 = 0
    temp = str(变量)
    for _ in temp:
        计数器 = 计数器 + 1
    计数器 = 计数器 * 1.2
    计数器 = str(计数器)
    计数器 = 计数器.split(".")[0]
    计数器 = int(计数器)
    计数器 = 计数器 + 22 + 计数器a
    print("=" * 计数器)
    print(日志(f"  ||（{颜色('变量名', 色选)}：{变量名}）"))
    print(日志(f"  ||（{颜色('数据', 色选)}：{变量}）"))
    print(日志(f"  ||（{颜色('类型', 色选)}: {变量类型}）"))
    print(日志(f"  ||（{颜色('位置', 色选)}:{行位置}）"))

    print("=" * 计数器 + "\n\n")


def 安全退出(内容, 变量=None):
    """
        FishConsole LOGS安全退出

        ----

        让整个模块使用统一的退出方式，不仅可以方便后期的管理，而且可以处理一些莫名奇妙的问题

        :param 内容: 要显示的文字
        :param 变量: 传入的变量（默认没有）
        :return: 显示你输入的文字并结束程序
        """
    a = sys._getframe(1).f_lineno
    if 变量 is None:
        sys.exit(日志(f"》Fishconsole {fcv.version()}安全退出》{内容} || line[{a}] ", "红色"))
    else:
        变量查看("temp", 变量)
        sys.exit(日志(f"》Fishconsole {fcv.version()}安全退出》{内容} || line[{a}] ", "红色"))


# print(日志(123, 色选="红色"))
# print(分割线("123","456","红色"))
# 全局参数="红色"
# a = finput("你你你你你你像个傻逼一样", 全局参数)
# 错误跟踪(["Fishconsole", "logs", "错误跟踪"], "笑死了","哈哈哈")
系统日志("用户调用了logs模块")
模块结束 = datetime.datetime.now()
系统日志(f'logs运行时间为：{模块结束 - 模块开始}')
