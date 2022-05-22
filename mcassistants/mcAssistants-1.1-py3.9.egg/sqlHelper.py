# -*- coding: utf-8 -*-


import pymysql
import sys
sys.path.append("..")


class MysqlUtil:
    def __init__(self, dbHost, dbPort,dbUser,dbPassword,dbName):
        self.cur = self.get_db(dbHost, int(dbPort),dbUser,dbPassword,dbName)

    def get_db(self, db_host, db_port, db_user, db_password, db_name):
        try:
            self.db = pymysql.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                db=db_name)
        except Exception as e:
            print(e)
            return
        cur = self.db.cursor()
        return cur

    # 查
    def query_execute(self, sql):

        try:
            self.cur.execute(sql)
            desc = self.cur.description  # 获取字段的描述，默认获取数据库字段名称，重新定义时通过AS关键重新命名即可
            data_dict = [dict(zip([col[0] for col in desc], row)) for row in self.cur.fetchall()]  # 列表表达式把数据组装起来
        except Exception as e:
            self.close()
            return {}
        self.close()
        return data_dict
    '''
    预发线上不能执行查以为的操作，暂时屏蔽
    '''
    # # 增、删、改
    # def execute_sql(self, sql):
    #     result = ''
    #     try:
    #         result = self.cur.execute(sql)
    #         self.db.commit()
    #     except Exception as e:
    #         print(e)
    #     if result == "":
    #         return False
    #     return True

    # 关闭数据库
    def close(self):
        self.db.close()
        
    def intToBin(self,number, index, feature=True):
        """index为该数据位宽,number为待转换数据,
        feature为True则进行十进制转二进制，为False则进行二进制转十进制。"""

        if (feature == True):  # 十进制转换为二进制
            if (number >= 0):
                b = bin(number)
                b = '0' * (index + 2 - len(b)) + b
            else:
                b = 2 ** (index) + number
                b = bin(b)
                b = '1' * (index + 2 - len(b)) + b  # 注意这里算出来的结果是补码
            b = b.replace("0b", '')
            b = b.replace('-', '')
            return b
        elif (feature == False):  # 二进制转换为十进制
            i = int(str(number), 2)
            if (i >= 2 ** (index - 1)):  # 如果是负数
                i = -(2 ** index - i)
                return i
            else:
                return i

    def tableId(self,storeId, maxId):
        a = self.intToBin(storeId, 64)
        b = '0' * 32 + a[0:32]
        c = ''
        for i in range(len(a)):
            if a[i] == b[i]:
                c += '1'
            else:
                c += '0'
        return ((int('0b' + c[32:], base=2))+1) % int(maxId)


if __name__ == '__main__':
    pass