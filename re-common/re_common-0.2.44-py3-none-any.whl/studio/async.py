"""
异步在python中的演变流程
"""

############################################################
# 第一步 python引入了迭代器的概念
############################################################

# 注意 iter 和 next方法
lists = [1, 2, 3, 4]
it = iter(lists)
print(next(it))
print(next(it))
print(next(it))
print(next(it))
print(next(it))  # StopIteration


# 类的迭代器实现
class MyNumbers(object):
    def __iter__(self):
        self.a = 1
        return self

    def __next__(self):
        if self.a <= 20:
            x = self.a
            self.a += 1
            return x
        else:
            raise StopIteration


myclass = MyNumbers()
myiter = iter(myclass)

for x in myiter:
    print(x)

############################################################
# 第二步 python引入了生成器的概念
############################################################


import sys


def fibonacci(n):  # 生成器函数 - 斐波那契
    a, b, counter = 0, 1, 0
    while True:
        if (counter > n):
            return
        yield a
        a, b = b, a + b
        counter += 1


f = fibonacci(10)  # f 是一个迭代器，由生成器返回生成

while True:
    try:
        print(next(f), end=" ")
    except StopIteration:
        sys.exit()
        break


# 使用了 yield 的函数被称为生成器
def consumer():
    r = 'start'
    while True:
        print("yield first")
        n = yield r
        print("n is %s,r is %s" % (n, r))
        print("yield end")
        if not n:
            return
        print('[CONSUMER] Consuming %s...' % n)
        r = '200 OK'


def produce(c):
    """
    由于生成器迭代器从生成器功能主体的顶部开始执行，因此在刚刚创建生成器时，没有yield表达式来接收值。
    因此，在生成器迭代器刚刚启动时，禁止使用non-None参数调用send（），如果发生这种情况，
    则引发TypeError（可能是由于某种逻辑错误）。因此，在与协程进行通信之前，
    必须首先调用next（）或send（None）将其执行推进到第一个yield表达式
    """
    re = c.send(None)
    print("************" + re)
    n = 0
    while n < 5:
        n = n + 1
        print('[PRODUCER] Producing %s...' % n)
        r = c.send(n)
        print('[PRODUCER] Consumer return: %s' % r)
    c.close()


c = consumer()
produce(c)


############################################################
# 第三步 python增强了生成器，引入 yield from
############################################################



# https://www.cnblogs.com/wongbingming/p/9085268.html
# yield from 是在Python3.3才出现的语法
# yield from 后面需要加的是可迭代对象，它可以是普通的可迭代对象，也可以是迭代器，甚至是生成器。

# 字符串
astr = 'ABC'
# 列表
alist = [1, 2, 3]
# 字典
adict = {"name": "wangbm", "age": 18}
# 生成器
agen = (i for i in range(4, 8))


def gen(*args, **kw):
    for item in args:
        for i in item:
            yield i


new_list = gen(astr, alist, adict, agen)
print(list(new_list))


# ['A', 'B', 'C', 1, 2, 3, 'name', 'age', 4, 5, 6, 7]

# 使用yield from
def gen(*args, **kw):
    for item in args:
        yield from item


new_list = gen(astr, alist, adict, agen)
print(list(new_list))


# ['A', 'B', 'C', 1, 2, 3, 'name', 'age', 4, 5, 6, 7]
# 由上面两种方式对比，可以看出，yield from后面加上可迭代对象，他可以把可迭代对象里的每个元素一个一个的yield出来，对比yield来说代码更加简洁，结构更加清晰。

# 生成器的嵌套

# 1、调用方：调用委派生成器的客户端（调用方）代码
# 2、委托生成器：包含yield from表达式的生成器函数
# 3、子生成器：yield from后面加的生成器函数
# 子生成器
def average_gen():
    total = 0
    count = 0
    average = 0
    while True:
        new_num = yield average
        count += 1
        total += new_num
        average = total / count


# 委托生成器
def proxy_gen():
    while True:
        yield from average_gen()


# 调用方
def main():
    calc_average = proxy_gen()
    next(calc_average)  # 预激下生成器
    print(calc_average.send(10))  # 打印：10.0
    print(calc_average.send(20))  # 打印：15.0
    print(calc_average.send(30))  # 打印：20.0


main()


# 子生成器
def average_gen():
    total = 0
    count = 0
    average = 0
    while True:
        new_num = yield average
        if new_num is None:
            break
        count += 1
        total += new_num
        average = total / count

    # 每一次return，都意味着当前协程结束。
    return total, count, average


# 委托生成器
def proxy_gen():
    while True:
        # 只有子生成器要结束（return）了，yield from左边的变量才会被赋值，后面的代码才会执行。
        total, count, average = yield from average_gen()
        print("计算完毕！！\n总共传入 {} 个数值， 总和：{}，平均数：{}".format(count, total, average))


# 调用方
def main():
    calc_average = proxy_gen()
    next(calc_average)  # 预激协程
    print(calc_average.send(10))  # 打印：10.0
    print(calc_average.send(20))  # 打印：15.0
    print(calc_average.send(30))  # 打印：20.0
    calc_average.send(None)  # 结束协程
    # 如果此处再调用calc_average.send(10)，由于上一协程已经结束，将重开一协程


main()


############################################################
# 第四步 python引入asyncio
############################################################

# asyncio是Python 3.4版本引入的标准库，直接内置了对异步IO的支持。
#
# asyncio的编程模型就是一个消息循环。我们从asyncio模块中直接获取一个EventLoop的引用，然后把需要执行的协程扔到EventLoop中执行，就实现了异步IO。
#
# 用asyncio实现Hello world代码如下：

import asyncio


@asyncio.coroutine
def hello():
    print("Hello world!")
    # 异步调用asyncio.sleep(1):
    r = yield from asyncio.sleep(1)
    print("Hello again!")


# 获取EventLoop:
loop = asyncio.get_event_loop()
# 执行coroutine
loop.run_until_complete(hello())
loop.close()

# @asyncio.coroutine把一个generator标记为coroutine类型，然后，我们就把这个coroutine扔到EventLoop中执行。
#
# hello()会首先打印出Hello world!，然后，yield from语法可以让我们方便地调用另一个generator。由于asyncio.sleep()也是一个coroutine，所以线程不会等待asyncio.sleep()，而是直接中断并执行下一个消息循环。当asyncio.sleep()返回时，线程就可以从yield from拿到返回值（此处是None），然后接着执行下一行语句。
#
# 把asyncio.sleep(1)看成是一个耗时1秒的IO操作，在此期间，主线程并未等待，而是去执行EventLoop中其他可以执行的coroutine了，因此可以实现并发执行。
#
# 我们用Task封装两个coroutine试试：

import threading
import asyncio


@asyncio.coroutine
def hello():
    print('Hello world! (%s)' % threading.currentThread())
    yield from asyncio.sleep(1)
    print('Hello again! (%s)' % threading.currentThread())


loop = asyncio.get_event_loop()
tasks = [hello(), hello()]
loop.run_until_complete(asyncio.wait(tasks))
loop.close()

"""
Hello world! (<_MainThread(MainThread, started 140735195337472)>)
Hello world! (<_MainThread(MainThread, started 140735195337472)>)
(暂停约1秒)
Hello again! (<_MainThread(MainThread, started 140735195337472)>)
Hello again! (<_MainThread(MainThread, started 140735195337472)>)
"""

############################################################
# 第五步 使用python内部关键词替换，变得简便
############################################################
# 用asyncio提供的@asyncio.coroutine可以把一个generator标记为coroutine类型，然后在coroutine内部用yield from调用另一个coroutine实现异步操作。

# 为了简化并更好地标识异步IO，从Python 3.5开始引入了新的语法async和await，可以让coroutine的代码更简洁易读。

# 请注意，async和await是针对coroutine的新语法，要使用新的语法，只需要做两步简单的替换：

# 把@asyncio.coroutine替换为async；
# 把yield from替换为await。
# 让我们对比一下上一节的代码：
import asyncio


@asyncio.coroutine
def hello():
    print("Hello world!")
    r = yield from asyncio.sleep(1)
    print("Hello again!")


# 用新语法重新编写如下：

async def hello2():
    print("Hello world!")
    r = await asyncio.sleep(1)
    print("Hello again!")
# 剩下的代码保持不变

# 看下这篇　比较明白
# https://blog.csdn.net/Likianta/article/details/90123678