import time


def name():
    """
    from lzlzhn import name
    name.name()
    please input your real name
    """
    name = input('请输入你的真实的名字/please input your real name' + '\n')
    if name == '谷柏慧':
        print('你来啦，给你准备的小惊喜还喜欢么')
        time.sleep(1.5)
        print('你是我最好的朋友')
        time.sleep(1.5)
        print('看到这个给我发微信，有惊喜哦')
        time.sleep(1.5)
    elif name == '卞觉':
        print('哦吼，你来啦，卞觉')
    elif name == '刘喜睿':
        print('呵呵')
    else:
        sex = input('你的性别？是男的还是女的？（输入男/女）/Your sex？  Male or Female？')
        if sex == 'Male' or sex == '男':
            print('你好呀，兄弟，欢迎你使用我的第三方模块，使用guide看看我的模块都有什么功能吧！')
            print('Hello, bro, welcome to use my third-party module, use the guide module to see what my module has!')
        elif sex == '女' or sex == 'Female':
            print('你好呀，美女，欢迎你使用我的第三方模块，使用guide看看我的模块都有什么功能吧！')
            print('Hello, lady, welcome to use my third-party module, use the guide module to see what my module has!')
        else:
            print('你输入的不正确请检查')
            print('Please check if you entered it incorrectly')
            exit_1 = input('退出按任意键 /Press any key to exit')
            if exit_1:
                exit()
