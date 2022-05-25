import random
def get_garbages():
    garbage_list = ["报纸","图书","期刊","塑料袋","玻璃瓶","易拉罐","废弃衣服","书包","鞋","矿泉水瓶",'螺丝刀','鱼骨头','糖果','菜叶','剩菜','花瓣','果皮','火锅汤底','茶渣','面包','蔬菜','鸡肉','电池','荧光灯管','灯泡','水银温度计','油漆桶','过期药品','过期化妆品','过期指甲油','染发剂','药片','消毒剂','眼镜','胶带','陶瓷花盆','渣土','卫生间废纸','纸巾','旧毛巾','尘土','橡皮泥','头发','创可贴']
    # 垃圾数量
    garbage_num = random.randint(8,10)
    # 产生随机垃圾
    random_garbage = []
    # 垃圾的索引列表，避免产生重复垃圾
    single_garbage_list = []

    for i in range(garbage_num):
        # 产生随机索引
        num = random.randint(0, len(garbage_list) - 1)
        # 如果垃圾索引不重复
        if num not in single_garbage_list:
            random_garbage.append(garbage_list[num])
            single_garbage_list.append(num)

    return random_garbage



def check_garbage(i):
    # 可回收垃圾
    list1 = ["报纸","图书","期刊","塑料袋","玻璃瓶","易拉罐","废弃衣服","书包","鞋","矿泉水瓶",'螺丝刀']
    # 湿垃圾（厨余垃圾）
    list2 = ['鱼骨头','糖果','菜叶','剩菜','花瓣','果皮','火锅汤底','茶渣','面包','蔬菜','鸡肉']
    # 有害垃圾
    list3 = ['电池','荧光灯管','灯泡','水银温度计','油漆桶','过期药品','过期化妆品','过期指甲油','染发剂','药片','消毒剂']
    # 干垃圾（其他垃圾）
    list4 = ['眼镜','胶带','陶瓷花盆','渣土','卫生间废纸','纸巾','旧毛巾','尘土','橡皮泥','头发','创可贴']
    if i in list1:
        return "1"
    if i in list2:
        return "2"
    if i in list3:
        return "3"
    if i in list4:
        return "4"
