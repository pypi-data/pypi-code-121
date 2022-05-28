def reg():
    pa = 0
    us = 0
    register = str(input("请输入注册用户名:"))
    string = "~!@#$%^&*()_+-*/<>,.[]\/"
    for i in string:
        if i in register:
            pa = 1
            print("您的用户名包含特殊字符")
    regpass = str(input("请输入注册密码:"))
    for i in string:
        if i in regpass:
            print("您的用户名包含特殊字符")
            us = 1
    if register == regpass:
        print("用户名与密码不得一致")
    if pa ==1 or us ==1:
        reg()
    if pa ==0 and us ==0 and register !=regpass:
        with open("textbook.txt", "a") as f:
            f.write("\n-------------------------------------我是分割线-----------------------------------------\n")
            for i in register and regpass:
                f.write(i)
