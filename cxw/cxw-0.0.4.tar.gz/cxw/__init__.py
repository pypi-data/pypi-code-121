import sys
import linecache

def my_excepthook(exctype, value, tb):
    print("[cxw] 阿 门 ~ 你的程序又报错了！")
    msg = "以下为错误详情 (Traceback)：\n"
    while tb:
        filename = tb.tb_frame.f_code.co_filename
        lineno = tb.tb_lineno
        name = tb.tb_frame.f_code.co_name
        # 判断是否为shell模式
        if (filename != "<stdin>"):
            msg += "  文件 \"%s\" 的第 %s 行，在 %s 内：\n" % (filename, lineno, name)
            msg += "    %s\n" % linecache.getline(filename, lineno).strip()

        tb = tb.tb_next
   
    err_msg = "错误信息："
    if exctype == ZeroDivisionError:
        err_msg = "你把一个数除以了零！数学是体育老师教的吗？"
    elif exctype == SyntaxError:
        err_msg = "有语法错误！仔细检查检查。"
    elif exctype == NameError:
        err_msg = "使用了未定义的变量！是不是变量名打错了呢？"
    elif exctype == TypeError:
        err_msg = "类型错误！是不是又用“+”连接数字和字符串了？"
    elif exctype == AttributeError:
        err_msg = "对象没有这个属性！"
    elif exctype == KeyboardInterrupt:
        err_msg = "你用Ctrl-C终止了程序！"
    print(msg + err_msg)
    print(exctype.__name__ + ": " + str(value))


sys.excepthook = my_excepthook

print("[cxw] 您成功导入了cxw包 (由xaz同学编写)")
print("[cxw] 程序开始运行，但愿不会报错。\n")
