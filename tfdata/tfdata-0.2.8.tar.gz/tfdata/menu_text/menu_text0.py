

intro_text = '欢迎使用TopFintech数据API。所有数据由人工智能程序收集、整理、计算，仅供参考。申请免费账户：添加微信公众号TFquant,对话栏输入"入会"。新手请查阅用户手册：http://www.topfintech.org/TF_API。屏蔽本登录提示: self.__init__(slient=True)'
att_text = 'att\n 简介: 数据标签即用于描述、指定某一集合数据的简称，例如"close", "vol", "turnover". 数据标签常作为参数用于TopFintech数据获取函数。查阅具体支持的标签名录及说明,可通过self.get_menu({数据函数命令}_att)了解, 多个数据标签可以列表格式输入'
usage_text = 'usage\n简介: 用于记录用户数据用量单位。一个单位等于一个表格单元。例如用户获得一个len=10的list数据，用量为10，一个4*4的pd.DataFrame表格则用量为16。用量到达限制可能无法继续获取数据，用量一般每日清零。'
date_range_text = 'date_range\n简介: 交易日序列指一个有序(从早到近期)的交易日日期集合，例如["2021-11-23","2021-11-24", ...... "2021-11-30"]. TopFintech 服务器根据 start_date, end_date, sample_size 三个参数生产交易日序列. 用户一般只需要提供其中两个参数值.例如，end_date = "2021-11-30", sample_size = 10,组合表示 以"2021-11-30"日为结束日，往前10个交易日的序列; start_date = "2021-05- 01", end_date="2021-10-01" 表示包含在两个日期间的交易日序列, 在这种情况下sample_size 参数输入将被忽略.'
code_text = 'code\n简介:TopFintech服务器接受的证券代码格式一般为 "{官方交易代码}.{后缀}"，例如: "000001.SZ"。股票、ETF代码后缀包括:SH,SZ,BJ(证券挂牌市场),中国市场指数后缀为"CNi",ETF期权后缀".CNo", 可转债后缀".SZb" 或 ".SHb"。'
login_text = '\n简介: 用户登录函数，向用户服务器请求分配数据服务器，须提供合法的TopFintech用户名、数据密码(获取账户:http://www.topfintech.org/user_management)\n参数: acct - 用户名,必填;pw - 数据密码,必填\n 登录信息或错误提示'
get_menu_text = 'get_menu\n简介:获取使用说明文本; 输入数据函数命令作为关键字, 可得关于该函数的说明文本\n参数：keyword - 说明文本关键字, 例如, 数据函数名, 参数等，必填; printout - 默认True,直接打印文本, 选False返回文本,选填\n返回：None or 说明文本'
get_tick_text = 'get_tick\n简介: 提供个股、ETF、ETF期权、可转债历史交易日日内跳价数据\n参数：code - 证券代码,必填,详阅self.get_menu("code"), date - 日期,格式yyyy-mm-dd,必填; timeout - 等待服务器返回数据的最长时秒, 默认200秒\n返回：时间序列表格, 其中volume_I跳价成交量单位为手，amt_I跳价成交额单位为千, dir_I = 0,1,-1 分别为中性，买入，卖出交易.'
get_hf5_text =  'get_hf5\n简介: 提供个股、ETF、ETF期权、可转债历史日内5档报价行情数据\n参数：code - 证券代码,必填,详阅self.get_menu("code"), date - 日期,格式yyyy-mm-dd,必填; timeout - 等待服务器返回数据的最长时秒, 默认200秒\n返回：时间序列表格, 其中volume_I累计成交量，单位为手，amt_I累计成交额,5档行情单量size单位为手，open_I当日开盘价, pre_close昨收'
get_min_text = 'get_min\n简介: 提供个股、ETF历史日内1分钟行情数据\n参数：code - 证券代码,必填，详阅self.get_menu("code"), date - 日期,格式yyyy-mm-dd,必填; timeout - 等待服务器返回数据的最长时秒, 默认200秒\n返回：时间序列表格, 其中vol_min时间段成交量，单位为手,amount_min时间段成交额,单位为千, 日间累计净买额单位为千'
get_1d_text = 'get_1d\n简介: 单维数据指以列表、字典、文本等集合数据格式呈现的，不含日期index序列的数据集合\n参数：att - 数据标签,必填. 了解函数目前支持的数据标签目录，见self.get_menu("get_1d_att"); timeout – 等待服务器返回数据的最长时秒, 默认 200 秒'
get_daily_text = 'get_daily\n简介: 提供股票、ETF、指数，OHLC,成交额、成交量日线数据\n参数：code - 证券代码,必填，详阅self.menu("code"); start_date/end_date/sample_size - 交易日序列参数，必填，详见self.menu("date_range"); adj_price - 返回前复权(q), 后复权(h), 或按指定日期中间复权的价格, 注意, 复权价根据pindex值进行反向推导, 该方法与通讯达等软件算法不同, 前者更贴实际收益, 默认不作复权处理; timeout - 等待服务器返回数据的最长时秒, 默认200秒\n返回：时间序列表格日线数据'
get_daily_pro_text = 'get_daily_pro\n简介: 提供股票、ETF、指数，日线扩展数据，对比于get_daily函数, get_daily_pro 可供用户自行设定返回表格数据中的标签变量,了解目前支持的日线数据标签见self.get_menu("get_daily_pro_att") \n参数：code - 证券代码,必填，详阅self.get_menu("code"); start_date/end_date/sample_size - 交易日序列参数，必填，详见self.get_menu("date_range"); att, 必填, 详见self.get_menu("att"),timeout - 等待服务器返回数据的最长时秒, 默认200秒\n返回：时间序列表格日线数据'


menu_basic_cn = {'intro':intro_text,
                 'code':code_text,
                 'att':att_text,
                 'usage':usage_text,
                 'date_range':date_range_text,
                 'code':code_text,
                 'login':login_text,
                 'get_menu':get_menu_text,
                 'get_1d':get_1d_text,           
                 'get_daily':get_daily_text,
                 'get_daily_pro':get_daily_pro_text,      
                 'get_tick':get_tick_text,
                 'get_hf5':get_hf5_text,
                 'get_min': get_min_text
                 }
