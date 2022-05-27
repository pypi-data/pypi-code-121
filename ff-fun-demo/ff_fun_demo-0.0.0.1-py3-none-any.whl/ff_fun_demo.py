import datetime
from fake_useragent import UserAgent
class operation_list(object):
    '''列表操作功能'''
    def division_list(list,nub):
        list_name=[]
        if len(list)%nub==0:
            for i in range(0,len(list),int(len(list)/nub)):
                name = list[i:i + int(len(list)/nub)]
                list_name.append(name)
        else:
            for i in range(0,len(list),int(len(list)/nub)+1):
                name = list[i:i + int(len(list)/nub)+1]
                list_name.append(name)
        return      list_name
class operation_time(object):
    '''时间操作功能'''
    def getdate(beforeOfDay):
        today = datetime.datetime.now()
            # 计算偏移量
        offset = datetime.timedelta(days=-beforeOfDay)
                # 获取想要的日期的时间
        re_date = (today + offset).strftime('%Y-%m-%d')
        return re_date
class   operation_Reptile(object):
    '''爬虫操作'''
    def getUa():
        try:
            ua = UserAgent()
            user_agent = ua.random
            return user_agent
        except Exception as e:
            pass
if __name__ == '__main__':
    print(operation_Reptile.getUa())

       


