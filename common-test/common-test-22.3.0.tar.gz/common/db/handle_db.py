import pymysql
from loguru import logger



class MysqlDB:

    conn = None

    def __init__(self, config):
        """初始化连接Mysql"""
        self.conn = pymysql.connect(
            host=config.get("host"),
            port=config.get("port"),
            user=config.get("user"),
            password=config.get("password"),
            db= config.get("db_name"),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )


    def fetch_one(self, sql: str) -> object:
        """查询数据，查一条"""
        with self.conn.cursor() as cur:
            cur.execute(sql)
            result = cur.fetchone()
            # 使用commit解决查询数据出现概率查错问题
            self.conn.commit()
        return result

    def execute(self, query_string: str):
        """
        只允许执行 SELECT 与 INSERT 语句
        """
        single_query = query_string.split(';')[0]
        logger.info('Mysql准备执行sql语句，%s' % single_query)
        sql_type = single_query.strip().split(" ")[0].lower()  # 从语句中提取第一个字符串判断sql类型。
        if "select" == sql_type or "insert" == sql_type or "delete":
            cursor = self.conn.cursor()
            cursor.execute(single_query)
            logger.info("Mysql sql执行成功")
            return cursor
        else:
            logger.error("不支持其他语句类型执行，请检查sql")

    def close(self):
        """关闭数据库连接"""
        self.conn.close()


if __name__ == '__main__':
    dict1={"host":"10.92.80.147","db_name":"traffic_test","port":3306,"user":"mysql","password":"test1234"}
    print(MysqlDB(dict1).execute("select * from base_test_res").fetchall())

