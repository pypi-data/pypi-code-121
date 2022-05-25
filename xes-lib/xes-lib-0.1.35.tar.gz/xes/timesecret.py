from time import *
year,month,day="2009","1","1"
mylist=[
    "看两页书",
    "背俩单词",
    "给朋友一个微笑",
    "做个自我介绍"
        ]
def birthday(name,y,m,d):
    global year,month,day
    year=y
    month=m
    day=d
    year=int(year)   #输入年份
    list1=["鼠","牛","虎","兔","龙","蛇","马","羊","猴","鸡","狗","猪"]   #生肖列表
    b=(year-4)%12    #计算生肖顺序
    a=list1[b]    #从列表中找到生肖
    if a=="鼠":
        x="性格乖巧，容易相处，学习努力，生活节俭。"
    if a=="牛":
        x="责任心强，勤奋踏实，富有创意，热爱工作。"
    if a=="虎":
        x="独立自强，富有主见，有正义感，责任心强。"
    if a=="兔":
        x="温和谦虚，潇洒机智，学习认真，一丝不苟。"
    if a=="龙":
        x="喜冒险，富有梦想，热爱奋斗，善于管理。"
    if a=="蛇":
        x="外冷内热，好奇心强，意志坚定，好学上进。"
    if a=="马":
        x="永不服输，热爱表达，容易相处，心直口快。"
    if a=="羊":
        x="性情温柔，风度优雅，为人正直，待人亲切。"
    if a=="猴":
        x="热爱进取，聪明能干，专注事业，敢于冒险。"
    if a=="鸡":
        x="头脑灵活，反应敏锐，喜爱旅行，乐于创造。"
    if a=="狗":
        x="谦虚谨慎，充满正义，忠诚可靠，热爱生活。"
    if a=="猪":
        x="头脑冷静，天真浪漫，性格温和，待人热情。"
    return "*******************\n"+name+'\n你的生日是:'+str(year)+"年"+str(month)+"月"+\
          str(day)+"日。\n你的属相是:"+a+"\n你的性格特征是："+x
    
def count(age=100):
    global year,month,day
    year=int(year)
    month=int(month)
    day=int(day)
    #daynow今天从ad经过多少天，daybirth为出生时ad经历时间，daytotal为生命天数
    daynow=localtime()[0]*365+localtime()[1]*30+localtime()[2]
    daybirth=year*365+month*30+day
    daytotal=age*365 
    dayspend=daynow-daybirth#经过的天数
    daylast=daytotal-dayspend #剩余天数
    ratiospend=str(round(dayspend/daytotal*100,2))+"%"
    ratiolast=str(round(daylast/daytotal*100,2))+"%"
    s1="*******************\n"+"你从出生到现在共经历的天数:"+str(dayspend)+"; 假如生命为:"+str(age)+"年，你的生命剩余天数:"+\
         str(daylast)+"; 你已经度过了生命的："+str(ratiospend)+"剩余生命的："+str(ratiolast)
    return s1
def study(name="爷爷",y1=1963,m1=6,d1=10):
    global year,month,day
    year=int(year)
    month=int(month)
    day=int(day)
    day1=y1*365+m1*30+d1
    day2=year*365+month*30+day
    daynow=localtime()[0]*365+localtime()[1]*30+localtime()[2]
    daydif=day2-day1
    s1 = ""
    if daydif>0:
        s1 = "******************\n你的学习对象是：" + name + "\n他的出生日期是：" + str(y1) + "年" + str(m1) + "月" + \
             str(d1) + "日。\n他/她的生命经历的天数："+str(daynow-day1)+\
          "\n比你的生命多经历的天数为：" + str(daydif) + "\n你要多向他学习，这是时间的价值"
    else:
        s1 = "三人行必有我师，即使年龄比我小，依然有值得学习的地方。"
    return s1
def welldone(my_list=mylist):
    print("****************\n我一分钟可以做的事情：")
    for i in my_list:
        print(i)
    print("珍惜时间，利用好每一分钟，我们会更加优秀！生命会更加精彩！")







