import random
def randomInt_Float(fromInt,toInt):
    randomnum = random.uniform(fromInt,toInt)
    return randomnum
def randomInt_Integers(fromInt,toInt):
    randomnumber = random.randint(fromInt,toInt)
    return randomnumber
def randomInt_type_MaxMinNumber():
    #使用循环取值支持输入，并检测异常，冒泡输入8位
    list_1 = list()
    try:
        for i in range(8):
            num = eval(input('请输入数字'))
            list_1.append(num)
        print(list_1)
        c = list_1[0]
        list_max = max(list_1)
        list_min = min(list_1)
        print('max:',list_max)
        print('min:',list_min)
    except Exception as e:
        print(e)
    return
def randomnumber_OneHundred():
    list_1 = list()
    index = 0
    for i in range(100):
        index = index + 1
        list_1.append(index)
    number = random.choice(list_1)
    return number
def randomnumber_Ten():
    list_1 = list()
    index = 0
    for i in range(10):
        index = index + 1
        list_1.append(index)
    number = random.choice(list_1)
    return number
def randomnumber_OneHhousand():
    list_1 = list()
    index = 0
    for i in range(1000):
        index = index + 1
        list_1.append(index)
    number = random.choice(list_1)
    return number
def randomnumber_TenHhousand():
    list_1 = list()
    index = 0
    for i in range(10000):
        index = index + 1
        list_1.append(index)
    number = random.choice(list_1)
    return number
def randomnumber_OneHundredHhousand():
    list_1 = list()
    index = 0
    for i in range(100000):
        index = index + 1
        list_1.append(index)
    number = random.choice(list_1)
    return number
def randomnumber_OneMillion():
    list_1 = list()
    index = 0
    for i in range(1000000):
        index = index + 1
        list_1.append(index)
    number = random.choice(list_1)
    return number
def randomnumber_TenMillion():
    list_1 = list()
    index = 0
    for i in range(10000000):
        index = index + 1
        list_1.append(index)
    number = random.choice(list_1)
    return number
def randomnumber_OneHundredMillion():
    list_1 = list()
    index = 0
    for i in range(100000000):
        index = index + 1
        list_1.append(index)
    number = random.choice(list_1)
    return number
def randomnumber_OneHundredMillion():
    list_1 = list()
    index = 0
    for i in range(100000000):
        index = index + 1
        list_1.append(index)
    number = random.choice(list_1)
    return number
def randomnumber_OneBillion():
    list_1 = list()
    index = 0
    for i in range(1000000000):
        index = index + 1
        list_1.append(index)
    number = random.choice(list_1)
    return number
def randomnumber_TenBillion():
    number = random.randint(1,10000000000)
    return number
def randomnumber_OneHundredBillion():
    number = random.randint(1,10000000000)
    return number
