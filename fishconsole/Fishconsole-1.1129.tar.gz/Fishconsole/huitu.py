"""
这是Fishconsole Project的matplilib中文辅助模块

----

为什么这个没有简洁？

我靠，我写的参数还不够明确啊？

主要是这个太大了，我没心情写

"""

import datetime
模块开始 = datetime.datetime.now()

import matplotlib.pyplot as plt
from Fishconsole import Fishsys
from Fishconsole import logs

logs.系统日志("用户调用了huitu模块")

def 单线折线图(x轴范围, x轴数据源: list, y轴范围, y轴数据源: list, 网格线=False, x轴名="x", y轴名="y", 线的样式="-", 线的颜色="b", 线的宽度=2, 画布长=6, 画布宽=6,
          标题=None,
          绘图标记=None, 网格线样式='-', 网格线方向="both", 网格线RGB="#000", 网格线宽度=0.5):
    a=Fishsys.强制类型检测(x轴数据源,"list")
    b=Fishsys.强制类型检测(y轴数据源,"list")
    if a:
        # noinspection PyStatementEffect
        1+1
    else:
        logs.安全退出("huitu》强制类型检测》单线折现图》请对x轴数据源使用list类型的数据")

    if b:
        # noinspection PyStatementEffect
        1+1
    else:
        logs.安全退出("huitu》强制类型检测》单线折现图》请对y轴数据源使用list类型的数据")
    # 修复可能出现的负数
    plt.rcParams['axes.unicode_minus'] = False
    # 画布长宽
    plt.figure(figsize=(画布长, 画布宽))
    # 配置字体
    plt.rcParams['font.sans-serif'] = ['SimHei']
    # 配置标题
    plt.title(标题)  # 括号当中输入标题的名称
    # x轴坐标轴范围
    plt.xlim(x轴范围)
    # y轴坐标轴范围
    plt.ylim(y轴范围)
    # x轴标签
    plt.xlabel(x轴名)
    # y轴标签
    plt.ylabel(y轴名)
    # 配置x轴和y轴的内容
    if 网格线:
        plt.grid(axis=f"{网格线方向}", color=网格线RGB, linewidth=网格线宽度, linestyle=网格线样式)
    x = x轴数据源
    y = y轴数据源
    plt.plot(x, y, linestyle=f'{线的样式}', color=f'{线的颜色}', marker=f'{绘图标记}', linewidth=f'{线的宽度}')
    plt.show()


def 双线折线图(x轴范围, x轴数据源: list, y轴范围, y轴数据源: list, xa轴范围, xa轴数据源: list, ya轴范围, ya轴数据源: list, 网格线=False, ya轴名="ya",
          xa轴名="xa", y轴名="y", x轴名="x",
          线的样式="-", 线的宽度=2, 画布长=6, 画布宽=6, 标题=None, 绘图标记=None, 网格线方向="both", 网格线样式='-', 网格线RGB="#000", 网格线宽度=0.5):
    a=Fishsys.强制类型检测(x轴数据源,"list")
    b=Fishsys.强制类型检测(y轴数据源, "list")
    c=Fishsys.强制类型检测(xa轴数据源, "list")
    d=Fishsys.强制类型检测(ya轴数据源, "list")
    if a:
        # noinspection PyStatementEffect
        1+1
    else:
        logs.安全退出("huitu》强制类型检测》双线折现图》请对x轴数据源使用list类型的数据")
    if b:
        # noinspection PyStatementEffect
        1+1
    else:
        logs.安全退出("huitu》强制类型检测》双线折现图》请对y轴数据源使用list类型的数据")
    if c:
        # noinspection PyStatementEffect
        1+1
    else:
        logs.安全退出("huitu》强制类型检测》双线折现图》请对xa轴数据源使用list类型的数据")
    if d:
        # noinspection PyStatementEffect
        1+1
    else:
        logs.安全退出("huitu》强制类型检测》双线折现图》请对ya轴数据源使用list类型的数据")
    # 修复可能出现的负数
    plt.rcParams['axes.unicode_minus'] = False
    # 画布长宽
    plt.figure(figsize=(画布长, 画布宽))
    # 配置字体
    plt.rcParams['font.sans-serif'] = ['SimHei']
    # 配置标题
    plt.title(标题)  # 括号当中输入标题的名称
    # x轴坐标轴范围
    plt.xlim(x轴范围)
    # y轴坐标轴范围
    plt.ylim(y轴范围)
    # xa轴标签
    plt.xlabel(x轴名)
    # y轴标签
    plt.ylabel(y轴名)
    # x轴坐标轴范围
    plt.xlim(xa轴范围)
    # y轴坐标轴范围
    plt.ylim(ya轴范围)
    # 标题的名称
    plt.title(标题)
    # x轴标签
    plt.xlabel(xa轴名)
    # y轴标签
    plt.ylabel(ya轴名)
    # 配置x轴和y轴的内容
    x = x轴数据源
    y = y轴数据源
    xa = xa轴数据源
    ya = ya轴数据源
    if 网格线:
        plt.grid(axis=f"{网格线方向}", color=网格线RGB, linewidth=网格线宽度, linestyle=网格线样式)
    plt.plot(x, y, xa, ya, linestyle=f'{线的样式}', marker=f'{绘图标记}', linewidth=f'{线的宽度}')
    plt.show()


# x轴数据源,y轴数据源,xa轴数据源,ya轴数据源,xb轴数据源,yb轴数据源,xc轴数据源,yc轴数据源,

def 子图(模式, 总标题=None, 子图a标题=None, 子图b标题=None, 子图c标题=None, 子图d标题=None, x轴数据源: list = None, y轴数据源: list = None,
       xa轴数据源: list = None,
       ya轴数据源: list = None, xb轴数据源: list = None, yb轴数据源: list = None, xc轴数据源: list = None, yc轴数据源: list = None,
       绘图标记: str = None,
       网格线方向="both", 网格线样式='-', 网格线RGB="#000", 网格线宽度=0.5, 网格线=False, x轴名="x", y轴名="y", xa轴名="xa", ya轴名="ya",
       xb轴名="xb", yb轴名="yb", xc轴名="xc", yc轴名="yc"):
    a=Fishsys.强制类型检测(x轴数据源, "list")
    b=Fishsys.强制类型检测(y轴数据源, "list")
    c=Fishsys.强制类型检测(xa轴数据源, "list")
    d=Fishsys.强制类型检测(ya轴数据源, "list")
    e=Fishsys.强制类型检测(xb轴数据源, "list")
    f=Fishsys.强制类型检测(yb轴数据源, "list")
    g=Fishsys.强制类型检测(xc轴数据源, "list")
    h=Fishsys.强制类型检测(xc轴数据源, "list")
    if a:
        # noinspection PyStatementEffect
        1+1
    else:
        logs.安全退出("huitu》强制类型检测》子图》请对x轴数据源使用list类型的数据")
    if b:
        # noinspection PyStatementEffect
        1+1
    else:
        logs.安全退出("huitu》强制类型检测》子图》请对y轴数据源使用list类型的数据")
    if c:
        # noinspection PyStatementEffect
        1+1
    else:
        logs.安全退出("huitu》强制类型检测》子图》请对xa轴数据源使用list类型的数据")
    if d:
        # noinspection PyStatementEffect
        1+1
    else:
        logs.安全退出("huitu》强制类型检测》子图》请对ya轴数据源使用list类型的数据")
    if e:
        # noinspection PyStatementEffect
        1+1
    else:
        logs.安全退出("huitu》强制类型检测》子图》请对xb轴数据源使用list类型的数据")
    if f:
        # noinspection PyStatementEffect
        1+1
    else:
        logs.安全退出("huitu》强制类型检测》子图》请对yc轴数据源使用list类型的数据")
    if g:
        # noinspection PyStatementEffect
        1+1
    else:
        logs.安全退出("huitu》强制类型检测》子图》请对xc轴数据源使用list类型的数据")
    if h:
        # noinspection PyStatementEffect
        1+1
    else:
        logs.安全退出("huitu》强制类型检测》子图》请对yc轴数据源使用list类型的数据")
    模式 = str(模式)
    if 模式 == "2":
        # 子图1
        xpoints = x轴数据源
        ypoints = y轴数据源
        plt.subplot(2, 2, 1)
        plt.plot(xpoints, ypoints)
        plt.title(f"{子图a标题}")
        # x轴标签
        plt.xlabel(x轴名)
        # y轴标签
        plt.ylabel(y轴名)
        # 修复可能出现的负数
        plt.rcParams['axes.unicode_minus'] = False
        # 配置字体
        plt.rcParams['font.sans-serif'] = ['SimHei']
        if 网格线:
            plt.grid(axis=f"{网格线方向}", color=网格线RGB, linewidth=网格线宽度, linestyle=网格线样式, marker=f'{绘图标记}')
        # 子图2
        x = xa轴数据源
        y = ya轴数据源
        plt.subplot(2, 2, 2)
        plt.plot(x, y)
        plt.title(f"{子图b标题}")
        # x轴标签
        plt.xlabel(xa轴名)
        # y轴标签
        plt.ylabel(ya轴名)
        # 修复可能出现的负数
        plt.rcParams['axes.unicode_minus'] = False
        # 配置字体
        plt.rcParams['font.sans-serif'] = ['SimHei']
        if 网格线:
            plt.grid(axis=f"{网格线方向}", color=网格线RGB, linewidth=网格线宽度, linestyle=网格线样式, marker=f'{绘图标记}')
        plt.suptitle(f"{总标题}")
        plt.show()

    if 模式 == "3":
        # 子图1
        xpoints = x轴数据源
        ypoints = y轴数据源
        plt.subplot(2, 2, 1)
        plt.plot(xpoints, ypoints)
        plt.title(f"{子图a标题}")
        # x轴标签
        plt.xlabel(x轴名)
        # y轴标签
        plt.ylabel(y轴名)
        # 修复可能出现的负数
        plt.rcParams['axes.unicode_minus'] = False
        # 配置字体
        plt.rcParams['font.sans-serif'] = ['SimHei']
        if 网格线:
            plt.grid(axis=f"{网格线方向}", color=网格线RGB, linewidth=网格线宽度, linestyle=网格线样式, marker=f'{绘图标记}')

        # 子图2
        x = xa轴数据源
        y = ya轴数据源
        plt.subplot(2, 2, 2)
        plt.plot(x, y)
        plt.title(f"{子图b标题}")
        # x轴标签
        plt.xlabel(xa轴名)
        # y轴标签
        plt.ylabel(ya轴名)
        # 修复可能出现的负数
        plt.rcParams['axes.unicode_minus'] = False
        # 配置字体
        plt.rcParams['font.sans-serif'] = ['SimHei']
        if 网格线:
            plt.grid(axis=f"{网格线方向}", color=网格线RGB, linewidth=网格线宽度, linestyle=网格线样式, marker=f'{绘图标记}')

        # 子图3
        x = xb轴数据源
        y = yb轴数据源
        plt.subplot(2, 2, 3)
        plt.plot(x, y)
        plt.title(f"{子图c标题}")
        # x轴标签
        plt.xlabel(xb轴名)
        # y轴标签
        plt.ylabel(yb轴名)
        # 修复可能出现的负数
        plt.rcParams['axes.unicode_minus'] = False
        # 配置字体
        plt.rcParams['font.sans-serif'] = ['SimHei']
        if 网格线:
            plt.grid(axis=f"{网格线方向}", color=网格线RGB, linewidth=网格线宽度, linestyle=网格线样式, marker=f'{绘图标记}')
        plt.suptitle(f"{总标题}")
        plt.show()

    if 模式 == "4":
        # 子图1
        xpoints = x轴数据源
        ypoints = y轴数据源
        plt.subplot(2, 2, 1)
        plt.plot(xpoints, ypoints)
        plt.title(f"{子图a标题}")
        # x轴标签
        plt.xlabel(x轴名)
        # y轴标签
        plt.ylabel(y轴名)
        # 修复可能出现的负数
        plt.rcParams['axes.unicode_minus'] = False
        # 配置字体
        plt.rcParams['font.sans-serif'] = ['SimHei']
        if 网格线:
            plt.grid(axis=f"{网格线方向}", color=网格线RGB, linewidth=网格线宽度, linestyle=网格线样式, marker=f'{绘图标记}')

        # 子图2
        x = xa轴数据源
        y = ya轴数据源
        plt.subplot(2, 2, 2)
        plt.plot(x, y)
        plt.title(f"{子图b标题}")
        # x轴标签
        plt.xlabel(xa轴名)
        # y轴标签
        plt.ylabel(ya轴名)
        # 修复可能出现的负数
        plt.rcParams['axes.unicode_minus'] = False
        # 配置字体
        plt.rcParams['font.sans-serif'] = ['SimHei']
        if 网格线:
            plt.grid(axis=f"{网格线方向}", color=网格线RGB, linewidth=网格线宽度, linestyle=网格线样式, marker=f'{绘图标记}')

        # 子图3
        x = xb轴数据源
        y = yb轴数据源
        plt.subplot(2, 2, 3)
        plt.plot(x, y)
        plt.title(f"{子图c标题}")
        # x轴标签
        plt.xlabel(xb轴名)
        # y轴标签
        plt.ylabel(yb轴名)
        # 修复可能出现的负数
        plt.rcParams['axes.unicode_minus'] = False
        # 配置字体
        plt.rcParams['font.sans-serif'] = ['SimHei']
        if 网格线:
            plt.grid(axis=f"{网格线方向}", color=网格线RGB, linewidth=网格线宽度, linestyle=网格线样式, marker=f'{绘图标记}')

        # 子图4
        x = xc轴数据源
        y = yc轴数据源
        plt.subplot(2, 2, 4)
        plt.plot(x, y)
        plt.title(f"{子图d标题}")
        # x轴标签
        plt.xlabel(xc轴名)
        # y轴标签
        plt.ylabel(yc轴名)
        # 修复可能出现的负数
        plt.rcParams['axes.unicode_minus'] = False
        # 配置字体
        plt.rcParams['font.sans-serif'] = ['SimHei']
        if 网格线:
            plt.grid(axis=f"{网格线方向}", color=网格线RGB, linewidth=网格线宽度, linestyle=网格线样式, marker=f'{绘图标记}')

        plt.suptitle(f"{总标题}")
        plt.show()


def 柱形图(x轴名: list, y轴数据: list, 背景: list = None, 模式="竖", 宽度=0.5, 高度=0.1, 标题=None, 网格线=False, 网格线方向="both", 网格线样式='-',
        网格线RGB="#000",
        网格线宽度=0.5):
    a=Fishsys.强制类型检测(x轴名, "list")
    b=Fishsys.强制类型检测(y轴数据, "list")
    c=Fishsys.强制类型检测(背景, "list")
    if a:
        # noinspection PyStatementEffect
        1+1
    else:
        logs.安全退出("huitu》强制类型检测》柱形图》请对x轴名使用list类型的数据")
    if b:
        # noinspection PyStatementEffect
        1+1
    else:
        logs.安全退出("huitu》强制类型检测》柱形图》请对y轴数据使用list类型的数据")
    if c:
        # noinspection PyStatementEffect
        1+1
    else:
        logs.安全退出("huitu》强制类型检测》柱形图》请对背景使用list类型的数据")
    if 模式 == "竖":
        plt.bar(x轴名, y轴数据, color=背景, width=宽度)
    else:
        plt.barh(x轴名, y轴数据, color=背景, height=高度)
    plt.title(f"{标题}")
    # 修复可能出现的负数
    plt.rcParams['axes.unicode_minus'] = False
    # 配置字体
    plt.rcParams['font.sans-serif'] = ['SimHei']
    if 网格线:
        plt.grid(axis=f"{网格线方向}", color=网格线RGB, linewidth=网格线宽度, linestyle=网格线样式)
    plt.show()


def 饼图(数据: list, 数据标签: list = None, 数据颜色: list = None, 总标题=None, 百分比=False):
    plt.pie(数据, labels=数据标签, colors=数据颜色)
    plt.title(总标题)  # 设置标题
    a=Fishsys.强制类型检测(数据, "list")
    b=Fishsys.强制类型检测(数据标签, "list")
    if a:
        # noinspection PyStatementEffect
        1+1
    else:
        logs.安全退出("huitu》强制类型检测》饼图》请对数据使用list类型的数据")
    if b:
        # noinspection PyStatementEffect
        1+1
    else:
        logs.安全退出("huitu》强制类型检测》饼图》请对数据标签使用list类型的数据")

    if 百分比:
        plt.pie(数据, labels=数据标签, colors=数据颜色, autopct='%.2f%%')
    # 修复可能出现的负数
    plt.rcParams['axes.unicode_minus'] = False
    # 配置字体
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.show()

模块结束 = datetime.datetime.now()
logs.系统日志(f'Fishsys运行时间为：{模块结束-模块开始}')