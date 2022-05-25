import random
def get_books():
    book_list = ['《我们的身体》','《神奇的校车》','《纸上动物园》','《地球之美》','《国家地理》','《十万个为什么》','《全球通史》','《美国史》','《史记》','《中国通史》','《中国近代史》','《 大国的兴衰》','《十年沧桑》','《边城》','《三体》','《撒哈拉的故事》','《白与黑》','《白夜行》','《月亮与六便士》','《肖申克的救赎》','《追风筝的人》','《奇点临近》','《盲眼钟表匠》','《上帝的手术刀》','《消失的微生物》','《癌症新知：科学终结恐慌》','《时间简史》','《从一到无穷大》']
    # 书数量
    book_num = random.randint(3,7)
    # 产生随机书
    random_book = []
    # 书的索引列表，避免产生重复书
    single_book_list = []

    for i in range(book_num):
        # 产生随机索引
        num = random.randint(0, len(book_list) - 1)
        # 如果书索引不重复
        if num not in single_book_list:
            random_book.append(book_list[num])
            single_book_list.append(num)

    return random_book



def check_book(i):
    # 科普类
    list1 = ['《我们的身体》','《神奇的校车》','《纸上动物园》','《地球之美》','《国家地理》','《十万个为什么》']
    # 历史类
    list2 = ['《全球通史》','《美国史》','《史记》','《中国通史》','《中国近代史》','《 大国的兴衰》','《十年沧桑》']
    # 小说类
    list3 = ['《边城》','《三体》','《撒哈拉的故事》','《白与黑》','《白夜行》','《月亮与六便士》','《肖申克的救赎》','《追风筝的人》']
    # 科技类
    list4 = ['《奇点临近》','《盲眼钟表匠》','《上帝的手术刀》','《消失的微生物》','《癌症新知：科学终结恐慌》','《时间简史》','《从一到无穷大》']
    if i in list1:
        return "1"
    if i in list2:
        return "2"
    if i in list3:
        return "3"
    if i in list4:
        return "4"
