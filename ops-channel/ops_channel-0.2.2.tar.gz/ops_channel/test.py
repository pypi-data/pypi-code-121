
from base import *


# a=cli.render('''
#    my name is {{name}}.
#    {%- for i in [1,2,3,4,5,6,7] %}
#     {{i}}
#    {%- endfor %}
# ''',{'name':"jqzhang"})
#
# # print(a)
#
#
# dsn='mysql://root:root@127.0.0.1:3306/test'
#
# conn=cli.get_mysql_connection(dsn)
# print(cli.mysql_query(conn,'show tables'))
# print(cli.mysql_query(conn,'select * from test'))