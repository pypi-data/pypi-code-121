# @Time    : 2022/2/11 16:52
# @Author  : kang.yang@qizhidao.com
# @File    : mysql_util.py
import pymysql


class BaseDB(object):
    def __init__(self, host, username, password, database):
        self.host = host
        self.username = username
        self.password = password
        self.database = database
        self.con = pymysql.connect(host=self.host,
                                   user=self.username,
                                   password=self.password,
                                   database=self.database,
                                   charset='utf8',
                                   )
        # cursorclass=pymysql.cursors.DictCursor
        # 该配置详会导致fetchone方法返回的是标题
        self.cursor = self.con.cursor()

    def insert(self, sql):
        try:
            self.cursor.execute(sql)
            self.con.commit()
        except Exception as e:
            print(f'插入失败: {e}')
            self.con.rollback()
        else:
            print('插入成功')
        finally:
            self.close()

    def delete(self, sql):
        try:
            self.cursor.execute(sql)
            self.con.commit()
        except Exception as e:
            print(f'删除失败: {e}')
            self.con.rollback()
        else:
            print('删除成功')
        finally:
            self.close()

    def update(self, sql):
        try:
            self.cursor.execute(sql)
            self.con.commit()
        except Exception as e:
            print(f'更新失败: {e}')
            self.con.rollback()
        else:
            print('更新成功')
        finally:
            self.close()

    def select(self, sql):
        try:
            self.cursor.execute(sql)
        except Exception as e:
            print(f'查询失败: {e}')
        else:
            print('查询成功,', end=' ')
            items = list(self.cursor.fetchall())
            print(f'共查询出: {len(items)} 行数据')
            return items
        finally:
            self.close()

    def close(self):
        self.cursor.close()
        self.con.close()








