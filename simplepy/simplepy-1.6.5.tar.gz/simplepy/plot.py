# -*- coding: UTF-8 -*-
import jieba
import matplotlib
import matplotlib.pyplot as plt
from wordcloud import WordCloud


def bar(title, counts, p_name, num=5):
    '''
    绘制柱状图的基础方法
    counts: 词频统计结果
    num: 绘制topN
    '''
    x_aixs = []
    y_aixs = []
    c_order = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    for c in c_order[:num]:
        x_aixs.append(c[0])
        y_aixs.append(c[1])

    # 解决中文显示问题
    plt.rcParams['font.family'] = ['sans-serif']
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
    plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题

    plt.bar(x_aixs, y_aixs)
    plt.title(title)
    plt.xticks(rotation=45)
    plt.savefig(f'{p_name}.png')
    plt.show()


def pie(title, data):
    """
    绘制饼图的基本方法
    :return:
    """
    plt.rcParams['font.sans-serif'] = 'SimHei'  # 设置中文显示
    plt.figure(figsize=(6, 6))  # 将画布设定为正方形，则绘制的饼图是正圆
    label = data.keys()  # 定义饼图的标签，标签是列表
    explode = [0.01] * len(data)  # 设定各项距离圆心n个半径
    values = data.values()
    plt.pie(values, explode=explode, labels=label, autopct='%5.1f%%')  # 绘制饼图
    plt.title(title)  # 绘制标题
    plt.savefig(f'{title}.jpg')  # 保存图片
    plt.show()


def line(title, x_la, y_la, data, p_name):
    """
    绘制折线图的基本方法
    :return:
    """

    # 处理乱码
    matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 用黑体显示中文
    x = list(data.keys())[:10]
    y = list(data.values())[:10]
    # "r" 表示红色，ms用来设置*的大小
    plt.plot(x, y, "r", marker='*', ms=10, label="a")
    # plt.plot([1, 二手车, 拉勾招聘, 基金], [20, 30, 80, 40], label="b")
    plt.xticks(rotation=45)
    plt.xlabel(x_la)
    plt.ylabel(y_la)
    plt.title(title)
    # upper left 将图例a显示到左上角
    plt.legend(loc="upper left")
    # 在折线图上显示具体数值, ha参数控制水平对齐方式, va控制垂直对齐方式
    for x1, y1 in zip(x, y):
        plt.text(x1, y1 + 1, str(y1), ha='center', va='bottom', fontsize=20, rotation=0)
    plt.savefig("{}.jpg".format(p_name))
    plt.show()


def word_cloud(content):
    """
    绘制词云的基本方法
    :param content: 内容
    :return:
    """
    max_content = ' '.join(jieba.cut(content))
    wordcloud = WordCloud(
        # 加载字体
        font_path="C:/Windows/Fonts/simfang.ttf",
        # 绘制的图像大小
        background_color="white", width=1000, height=880).generate(max_content)

    # 渲染显示
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig('公司待遇词语图.png')
    plt.show()


def mult_sub_plot():
    # 开始画图
    sub_axix = filter(lambda x: x % 200 == 0, x_axix)
    plt.title('Result Analysis')
    plt.plot(x_axix, train_acys, color='green', label='training accuracy')
    plt.plot(sub_axix, test_acys, color='red', label='testing accuracy')
    plt.plot(x_axix, train_pn_dis, color='skyblue', label='PN distance')
    plt.plot(x_axix, thresholds, color='blue', label='threshold')
    plt.legend()  # 显示图例

    plt.xlabel('iteration times')
    plt.ylabel('rate')
    plt.show()
    # python 一个折线图绘制多个曲线
