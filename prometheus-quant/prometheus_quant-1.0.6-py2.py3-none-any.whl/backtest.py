import abc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from tqdm import tqdm
from dash import dcc
from dash import html
from dash import Dash
from dash import dash_table
from datetime import datetime
from prometheus.base import protocol
from prometheus.callback import callback
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output
from prometheus.strategy import template as strategy_template


class template(callback):
    """回测基类"""
    def __init__(self):
        """初始化方法"""
        # 调用父类初始化方法
        super(template, self).__init__()
        # 是否显示进度
        self.__is_show_progress = True
        # 行情数据资源列表
        self.__quote_data_source_list =[]
        # 行情数据(总体存放的数据)
        self.__quote_data = None
        # 当前行情(按时间变化的全市场快照)
        self.__last_snapshot = None
        # 当前行情(当前播放的最新一个tick)
        self.__last_tick = None
        # 当前行情的时间
        self.__last_quote_datetime = None
        # 策略登记表{strategy_id: strategy}
        self.__strategy_registration_table = dict()
        # 配置文件登记表{strategy_id: setting_file_path}
        self.__setting_registration_table = dict()
        # 所有的订阅记录{instrument_id: set(strategy_id)}
        self.__subscription_registration_table = dict()

    def set_show_progress(self, enable: bool):
        """设置是否显示进度"""
        self.__is_show_progress = enable

    def last_snapshot(self) -> pd.DataFrame:
        """最新的快照"""
        return self.__last_snapshot

    def last_tick(self) -> dict:
        """最新的tick"""
        return self.__last_tick

    def last_quote_datetime(self) -> datetime:
        """最新的行情时间"""
        return self.__last_quote_datetime

    def last_quote_date(self) -> datetime:
        """最新的行情日期"""
        return self.__last_quote_datetime.replace(hour=0, minute=0, second=0, microsecond=0)

    def strategy_registration_table(self) -> dict:
        """查找策略"""
        return self.__strategy_registration_table

    def subscription_registration_table(self) -> dict:
        """订阅列表"""
        return self.__subscription_registration_table

    def add_quote_data_source(self, source: str):
        """添加行情数据资源"""
        self.__quote_data_source_list.append(source)

    def add_quote_data_source_list(self, source_list: list):
        """添加行情数据资源列表"""
        self.__quote_data_source_list.extend(source_list)

    def set_quote_data(self, quote_data: pd.DataFrame):
        """注册行情数据"""
        std_columns = {
            'Date', 
            'Time', 
            'MilliSecond', 
            'ExchangeID', 
            'InstrumentID', 
            'AskPrice1', 
            'AskVolume1', 
            'BidPrice1', 
            'BidVolume1', 
            'Preclose', 
            'Prevolume', 
            'OpenInterest', 
            'High', 
            'Open', 
            'Low', 
            'Last', 
            'Volume',
            'Amount', 
            'LimitDown', 
            'LimitUp', 
        }
        quote_data_columns = set(quote_data.columns.tolist())
        assert quote_data_columns & std_columns == std_columns, f"行情数据不符合需求规范，确实数据列: {std_columns-quote_data_columns}, 请先做处理后，再传入"

        # 数据排序,保存
        self.__quote_data = quote_data.sort_values(['Date', 'Time'])

    def register_strategy(self, strategy_id: str, strategy: strategy_template, setting_path: str):
        """注册策略"""
        # 防错，策略id必须唯一
        assert strategy_id not in self.__strategy_registration_table or strategy_id not in self.__setting_registration_table, f"{strategy_id}已存在记录中"
        
        # 记录
        self.__strategy_registration_table[strategy_id] = strategy
        self.__setting_registration_table[strategy_id] = setting_path
    
    def subscribe(self, strategy_id: str, exchange_id: str, instrument_id: str):
        """订阅任务入队列"""
        # 登记订阅信息
        if instrument_id not in self.__subscription_registration_table:
            self.__subscription_registration_table[instrument_id] = set()
        self.__subscription_registration_table[instrument_id].add(strategy_id)

        # 应答订阅成功
        self.__strategy_registration_table[strategy_id].on_subscribe(
            exchange_id=exchange_id, instrument_id=instrument_id, success=True
        )
    
    def unsubscribe(self, strategy_id: str, exchange_id: str, instrument_id: str):
        """退订任务入队列"""
        # 删除登记的订阅信息
        if instrument_id in self.__subscription_registration_table:
            self.__subscription_registration_table[instrument_id].discard(strategy_id)

        # 应答退订成功
        self.__strategy_registration_table[strategy_id].on_unsubscribe(
            exchange_id=exchange_id, instrument_id=instrument_id, success=True
        )
    
    def insert_order(self, strategy_id: str, order: dict):
        """报单任务入队列"""
        # 策略调用本接口，出发本类虚回调方法
        self.on_receive_new_insert(strategy_id, order)
    
    def cancel_order(self, strategy_id: str, order: dict):
        """撤单任务入队列"""
        # 策略调用本接口，出发本类虚回调方法
        self.on_receive_new_cancel(strategy_id, order)
    
    def query_instrument(self, strategy_id: str, exchange_id: str, instrument_id: str):
        """查询标的任务入队列"""
        pass
    
    def query_account(self, strategy_id: str):
        """查询账户任务入队列"""
        pass
    
    def query_position(self, strategy_id: str):
        """查询持仓任务入队列"""
        pass
    
    def stop_strategy(self, strategy_id: str):
        """停止指定策略"""
        # 判断该策略是否被登记
        if strategy_id not in self.__strategy_registration_table:
            return

        # 获取策略
        strategy = self.__strategy_registration_table[strategy_id]

        # 删除所有记录
        for instrument_id in self.__subscription_registration_table:
            self.__subscription_registration_table[instrument_id].discard(strategy_id)
        del self.__strategy_registration_table[strategy_id]
        del self.__setting_registration_table[strategy_id]

        # 回调该策略停止回调
        strategy.on_stop()
    
    @abc.abstractmethod
    def on_next_quote_source(self, source: str):
        """更新下一个行情资源"""
        pass

    @abc.abstractmethod
    def on_receive_new_snapshot(self):
        """当快照更新的时候的触发"""
        pass
    
    @abc.abstractmethod
    def on_receive_new_tick(self):
        """当快照中每一个tick推送时的更新"""
        pass

    @abc.abstractmethod
    def on_receive_new_insert(self, strategy_id: str, order: dict):
        """当收到新的报单请求"""
        pass

    @abc.abstractmethod
    def on_receive_new_cancel(self, strategy_id: str, order: dict):
        """当收到新的撤单请求"""
        pass

    @abc.abstractmethod
    def on_backtest_finished(self):
        """回测结束回调，由用户实现，可在此处显示回测报告"""
        pass

    def run(self):
        """回测启动运行"""
        # 初始化所有的策略
        for strategy_id in self.__strategy_registration_table:
            self.__strategy_registration_table[strategy_id].strategy_id = strategy_id
            self.__strategy_registration_table[strategy_id].callback = self
            self.__strategy_registration_table[strategy_id].on_init(
                self.__setting_registration_table[strategy_id]
            )

        # 启动所有策略，并设置回调对象
        for strategy_id in self.__strategy_registration_table:
            self.__strategy_registration_table[strategy_id].on_start()

        # 自动订阅所有的标的，并记录
        for strategy_id in self.__strategy_registration_table:
            # 依据登记的策略ID，查找策略对象
            strategy = self.__strategy_registration_table[strategy_id]
            # 遍历策略对象的自动订阅列表
            for exchange_id, instrument_id in strategy.subscription_list:
                # 登记订阅信息
                if instrument_id not in self.__subscription_registration_table:
                    self.__subscription_registration_table[instrument_id] = set()
                self.__subscription_registration_table[instrument_id].add(strategy_id)

        # 调取每一个行情资源
        for index, source in enumerate(self.__quote_data_source_list):
            # 资源处理回调函数
            print(f"加载第{index+1}个行情数据资源，共计{len(self.__quote_data_source_list)}个行情数据资源需要加载")
            self.on_next_quote_source(source)
            print(f"加载完毕，开始播放行情:")

            # 按时间播放每一帧行情快照
            if self.__quote_data is None or self.__quote_data.empty:
                continue
            if self.__is_show_progress:
                tqdm.pandas()
                self.__quote_data.groupby(["Date", "Time"]).progress_apply(self.__snapshot_handler)
            else:
                self.__quote_data.groupby(["Date", "Time"]).apply(self.__snapshot_handler)

        # 回测结束回调，由用户实现，可在此处显示回测报告
        self.on_backtest_finished()

    def __snapshot_handler(self, snapshot: pd.DataFrame):
        """播放行快照，处理函数"""
        # 将当前快照保留
        self.__last_snapshot = snapshot

        # 更新行情时间
        date = str(snapshot["Date"].max())
        time = str(snapshot["Time"].max())
        milli_second = "000"
        date = date.replace("/", "").replace("-", "").replace(":", "")
        time = time.replace("/", "").replace("-", "").replace(":", "")
        quote_datetime = datetime.strptime(
            f"{date} {time}.{milli_second}", 
            "%Y%m%d %H%M%S.%f"
        )
        self.__last_quote_datetime = quote_datetime if self.__last_quote_datetime is None else max(quote_datetime, self.__last_quote_datetime)

        # 先出发回调
        self.on_receive_new_snapshot()

        # 解析当前行情快照的每一笔行情
        snapshot.apply(self.__tick_handler, axis=1)

    def __tick_handler(self, tick: pd.Series):
        """播放行快照，处理函数"""
        # 解析行情
        instrument_id = tick["InstrumentID"]

        # 将行情格式转换为字典
        self.__last_tick = tick.to_dict()

        # 当前市行情时间
        date = str(self.__last_tick["Date"]).replace("/", "").replace("-", "").replace(":", "")
        time = str(self.__last_tick["Time"]).replace("/", "").replace("-", "").replace(":", "")
        milli_second = str(self.__last_tick["MilliSecond"])
        quote_datetime = datetime.strptime(
            f"{date} {time}.{milli_second}", 
            "%Y%m%d %H%M%S.%f"
        )
        self.__last_quote_datetime = quote_datetime if self.__last_quote_datetime is None else max(quote_datetime, self.__last_quote_datetime)

        # 触发回调
        self.on_receive_new_tick()

        # 查找有订阅的策略
        strategy_id_list = self.__subscription_registration_table.get(instrument_id, [])
        # 遍历所有的策略id
        for strategy_id in strategy_id_list:
            # 查找对应的策略，推送行情
            self.__strategy_registration_table[strategy_id].on_tick(self.__last_tick)


class ctp_backtest(template):
    """回测实例类"""
    def __init__(self):
        """初始化方法"""
        # 调用父类初始化方法
        super(ctp_backtest, self).__init__()

        # 默认参数
        self.__rate = 0.000025      # 手续费率
        self.__slippage = 0.2       # 交易滑点
        self.__size = 300           # 合约乘数
        self.__pricetick = 0.2      # 价格跳动
        self.__capital = 1000000    # 初始资金
        self.__annual_days = 240    # 年化天数
        self.__risk_free = 0        # 无风险利率

        # 报单记录表，key为(策略ID strategy_id，报单引用order_ref)，value为order字典，参照协议说明protocol.md
        self.__insert_order_table = dict()

        # 撤单请求记录表，key为(策略ID strategy_id，报单引用order_ref)，value为order字典
        self.__cancel_order_table = dict()

        # 逐日盯市交易记录，每次撮合成功之后，就会将结果放入这里，主要用于回测行情播放完毕之后，进行统计结算
        self.__trade_record_id = 0
        self.__trade_record_table = list()    # 元素为字典
        self.__trade_record_df = None         # self.__trade_record_table的DataFrame化

        # 逐日盯市结果计算
        self.__daily_close_table = dict()     # 每日，每个标的收盘价和昨收
        self.__daily_result_table = list()    # 每个策略，每日，每个标的上的统计
        self.__daily_result_df = None         # self.__daily_result_table的DataFrame化

        # 回测统计结果
        self.__backtest_statistics_result = dict()
        self.__backtest_statistics_result_df = None

    def set_rate(self, rate: float):
        """设置手续费率"""
        assert size >= 0, f"手续费率值非法"
        self.__rate = 0.000025

    def set_slippage(self, slippage: float):
        """设置交易滑点"""
        assert size >= 0, f"交易滑点值非法"
        self.__slippage = 0.2

    def set_size(self, size: int):
        """设置合约乘数"""
        assert size > 0, f"合约乘数值非法"
        self.__size = 300

    def set_pricetick(self, pricetick: float):
        """设置价格跳动"""
        assert size > 0, f"价格跳动值非法"
        self.__pricetick = 0.2

    def set_capital(self, capital: int):
        """设置初始资金"""
        assert size > 0, f"初始资金值非法"
        self.__capital = 1000000
        
    def set_risk_free(self, risk_free: int):
        """设置无风险利率"""
        assert risk_free > 0, f"无风险利率"
        self.__risk_free = risk_free

    def set_annual_days(self, annual_days: int):
        """设置年化天数"""
        assert annual_days > 0, f"年化天数"
        self.__annual_days = annual_days

    def on_receive_new_snapshot(self):
        """当快照更新的时候的触发"""
        # 记录当日所有标的的收盘价和昨收价
        self.__record_all_close()
        # 处理所有的撤单请求
        self.__do_cancel()
        # 尝试撮合
        self.__cross_orders()
        # 清理废单
        self.__clear_waste_order()
    
    def on_receive_new_tick(self):
        """当快照中每一个tick推送时的更新"""
        pass

    def on_receive_new_insert(self, strategy_id: str, order: dict):
        """当收到新的报单请求"""
        # 获取报单引用
        order_ref = order.get("OrderRef", None)

        # 如果没有报单引用，应答保单失败
        if order_ref is None:
            self.strategy_registration_table()[strategy_id].on_insert(order, True, "缺少报单引用order_ref")
            return

        # 如果同样的保单引用还在未成交报单列表中，应答保单失败
        if (strategy_id, order_ref) in self.__insert_order_table:
            self.strategy_registration_table()[strategy_id].on_insert(order, True, "报单引用order_ref重复")
            return

        # 记录报单请求，等待撮合
        order["InsertDateTime"] = self.last_quote_datetime()
        self.__insert_order_table[(strategy_id, order_ref)] = order
        # 应答策略的请求
        self.strategy_registration_table()[strategy_id].on_insert(order, True, "")

    def on_receive_new_cancel(self, strategy_id: str, order: dict):
        """当收到新的撤单请求"""
        # 获取报单引用
        order_ref = order.get(OrderRef, None)

        # 如果没有报单引用，应答保单失败
        if order_ref is None:
            self.strategy_registration_table()[strategy_id].on_cancel(order, True, "缺少报单引用order_ref")
            return

        # 如果同样的保单引用还在未成交报单列表中，应答保单失败
        if (strategy_id, order_ref) not in self.__insert_order_table:
            self.strategy_registration_table()[strategy_id].on_insert(order, True, "报单引用order_ref已经不在dui列中")
            return

        # 记录撤单请求，等待撤单执行
        self.__cancel_order_table[(strategy_id, order_ref)] = order
        # 应答策略的请求
        self.strategy_registration_table()[strategy_id].on_cancel(order, True, "")

    def on_backtest_finished(self):
        """回测结束之后的回调"""
        # 计算逐日盯市结果
        self.__calculate_daily_result()
        
        # 计算整个回测的数据统计结果
        self.__calculate_backtest_statistics_result()

    def show_report(self):
        """使用dash显示回测报告"""
        # 容错
        if self.__backtest_statistics_result_df is None or self.__backtest_statistics_result_df.empty:
            return
        if self.__daily_result_df is None or self.__daily_result_df.empty:
            return
        if self.__trade_record_df is None or self.__trade_record_df.empty:
            return
        # 将所有的报告的英文名称替换成中文
        self.__backtest_statistics_result_df.rename(columns={
            'StrategyID': '策略ID', 
            'InstrumentID': '交易标的', 
            'StartDate': '首个交易日', 
            'EndDate': '最后交易日', 
            'TotalDays': '总交易日', 
            'ProfitDays': '盈利交易日', 
            'LossDays': '亏损交易日', 
            'Capital': '起始资金', 
            'EndBalance': '结束资金', 
            'TotalReturn': '总收益率', 
            'AnnualReturn': '年化收益', 
            'MaxDrawdown': '最大回撤', 
            'MaxDdpercent': '百分比最大回撤', 
            'MaxDrawdownDuration': '最长回撤天数', 
            'TotalNetPnl': '总盈亏', 
            'TotalCommission': '总手续费', 
            'TotalSlippage': '总滑点', 
            'TotalTurnover': '总成交金额', 
            'TotalTradeCount': '总成交笔数', 
            'DailyNetPnl': '日均盈亏', 
            'DailyCommission': '日均手续费', 
            'DailySlippage': '日均滑点', 
            'DailyTurnover': '日均成交金额', 
            'DailyTrade_count': '日均成交笔数', 
            'DailyReturn': '日均收益率', 
            'ReturnStd': '收益标准差', 
            'SharpeRatio': '夏普比率', 
            'ReturnDrawdownRatio': '收益回撤比'
        }, inplace=True)
        self.__daily_result_df.rename(columns={
            'PreClosePrice': '昨日收盘价', 
            'ClosePrice': '当日收盘价', 
            'StrategyID': '策略ID', 
            'Date': '日期', 
            'InstrumentID': '交易标的', 
            'PositionChange': '当日仓位变化', 
            'Volume': '成交量', 
            'TradeCount': '交易计数', 
            'EndPosition': '当日收盘是的仓位', 
            'StartPosition': '当日开盘时的仓位', 
            'Turnover': '当日换手', 
            'Commission': '佣金', 
            'Slippage': '滑点', 
            'HoldingPnl': '持仓收益', 
            'TradingPnl': '交易收益', 
            'TotalPnl': '总收益', 
            'NetPnl': '净收益', 
            'Balance': '账户估值', 
            'HighLevel': '高点记录', 
            'Return': '当日收益', 
            'DrawDown': '当日回撤', 
            'Ddpercent': '当日百分比回撤'
        }, inplace=True)
        self.__trade_record_df.rename(columns={
            'Date': '日期', 
            'Datetime': '时间', 
            'StrategyID': '策略ID', 
            'TradeRecordID': '交易记录ID', 
            'InstrumentID': '交易标的', 
            'ExchangeID': '交易所', 
            'Direction': '买卖方向', 
            'Offset': '平仓类型', 
            'Price': '成交价格', 
            'Volume': '成交量', 
            'OrderRef': '报单引用'
        }, inplace=True)

        # 创建索引
        self.__backtest_statistics_result_df.insert(loc=0, column="策略-标的", value="")
        self.__daily_result_df.insert(loc=0, column="策略-标的", value="")
        self.__trade_record_df.insert(loc=0, column="策略-标的", value="")
        self.__backtest_statistics_result_df["策略-标的"] = self.__backtest_statistics_result_df.apply(lambda x: f"{x['策略ID']}-{x['交易标的']}", axis=1)
        self.__daily_result_df["策略-标的"] = self.__daily_result_df.apply(lambda x: f"{x['策略ID']}-{x['交易标的']}", axis=1)
        self.__trade_record_df["策略-标的"] = self.__trade_record_df.apply(lambda x: f"{x['策略ID']}-{x['交易标的']}", axis=1)

        # 创建标题
        title = html.H1(children=f"回测报告", style={"text-align": "center"})

        # 创建统计数据报告
        df = self.__backtest_statistics_result_df.set_index(["策略-标的"]).T.reset_index()
        df.rename(columns={"index": "项目"}, inplace=True)
        backtest_statistics_result_table = dash_table.DataTable(
            df.to_dict('records'), 
            [{"name": i, "id": i} for i in df.columns]
        )
        # 创建逐日盯市报告(账户净值)
        daily_result_balance_graph = dcc.Graph(
            id="daily_result_balance", 
            figure=px.line(
                self.__daily_result_df, 
                x="日期", 
                y="账户估值", 
                color="策略-标的",
                line_shape="linear", 
                title='账户净值',
                # width=1600,
                height=900
            )
        )
        # 创建逐日盯市报告(净值回撤)
        daily_result_drawdown_graph = dcc.Graph(
            id="daily_result_drawdown", 
            figure=px.line(
                self.__daily_result_df, 
                x="日期", 
                y="当日回撤", 
                color="策略-标的",
                line_shape="linear", 
                title='净值回撤',
                # width=1600,
                height=900
            )
        )
        # 创建逐日盯市报告(每日盈亏)
        daily_result_pnl_graph = dcc.Graph(
            id="daily_pnl_drawdown", 
            figure=px.bar(
                self.__daily_result_df, 
                x="日期", 
                y="净收益", 
                color="策略-标的",
                barmode="group", 
                title='每日盈亏',
                # width=1600,
                height=900
            )
        )
        # 创建逐日盯市报告(盈亏分布)
        def __cal_hist(row: pd.DataFrame):
            hist, x = np.histogram(row["净收益"], bins="auto")
            df_temp = pd.DataFrame({"盈亏": x[:-1], "数量": hist})
            df_temp.insert(loc=0, column="策略-标的", value=row["策略-标的"].iloc[0])
            return df_temp
        df = self.__daily_result_df.groupby(["策略-标的"]).apply(__cal_hist).reset_index(drop=True)
        daily_result_distribution_graph = dcc.Graph(
            id="daily_result_distribution", 
            figure=px.bar(
                df,
                x='盈亏',
                y='数量',
                color="策略-标的",
                barmode="group",
                title='盈亏分布',
                # width=1600,
                height=900
            )
        )

        # 交易记录报告
        # print(self.__trade_record_df)

        # 显示报告用的dash的app
        app = Dash(__name__)
        app.layout = html.Div(children=[
            title,
            backtest_statistics_result_table,
            daily_result_balance_graph,
            daily_result_drawdown_graph,
            daily_result_pnl_graph,
            daily_result_distribution_graph
        ])
        app.run_server(debug=False, threaded=True, port=7777)

    def __record_all_close(self):
        """记录当日所有标的的收盘价和昨收价"""
        # 按照标的丰足
        self.last_snapshot().groupby(["InstrumentID"]).apply(self.__record_close)

    def __record_close(self, symbol_snapshot: pd.DataFrame):
        """记录每个标的当日的收盘价和昨收价"""
        # 按时间排序，取最后一行数据
        tick = symbol_snapshot.sort_values(["Time"]).iloc[-1]
        
        # 获取行情日期
        date = self.last_quote_date()
        last_price = tick["Last"]
        instrument_id = tick['InstrumentID']

        # 创建逐日盯市数据初始
        if date not in self.__daily_close_table:
            self.__daily_close_table[date] = {}
        if instrument_id not in self.__daily_close_table[date]:
            self.__daily_close_table[date][instrument_id] = {
                "Date": date,
                "PreClosePrice": tick["Preclose"]
            }

        # 记录该标的当日收盘价
        self.__daily_close_table[date][instrument_id]["ClosePrice"] = last_price

    def __do_cancel(self):
        """执行所有的撤单请求"""
        # 遍历所有的撤单请求
        for strategy_id, order_ref in list(self.__cancel_order_table.keys()):
            # 如果报单还在待撮合队列中
            if (strategy_id, order_ref) in self.__insert_order_table:
                order = self.__insert_order_table[(strategy_id, order_ref)]
                order["OrderSubmitStatus"] = "Accepted"
                order["OrderStatus"] = "Canceled"

                del self.__insert_order_table[(strategy_id, order_ref)]
                del self.__cancel_order_table[(strategy_id, order_ref)]

                self.strategy_registration_table()[strategy_id].on_order(order)
            else:
                order = self.__cancel_order_table[(strategy_id, order_ref)]
                order["OrderSubmitStatus"] = "CancelRejected"
                order["OrderStatus"] = "AllTraded"

                del self.__cancel_order_table[(strategy_id, order_ref)]
                
                self.strategy_registration_table()[strategy_id].on_order(order)

    def __cross_orders(self):
        """所有订单尝试执行撮合"""
        # 最新时间
        last_datetime = self.last_quote_datetime()

        # 遍历所有的报单
        for strategy_id, order_ref in list(self.__insert_order_table.keys()):
            # 提取订单
            order = self.__insert_order_table[(strategy_id, order_ref)]

            # 提取订单标的
            instrument_id = order["InstrumentID"]

            # 提取订单标的交易方向
            direction = order["Direction"]

            # 获取该标的的最新价
            snapshot_df = self.last_snapshot()
            symbol_snapshot_df = snapshot_df[snapshot_df["InstrumentID"] == instrument_id]
            last_price = symbol_snapshot_df["Last"].iloc[-1]

            # 获取止盈止损单的出发价格
            stop_price = order.get("StopPrice", None)

            # 判断报单的撮合触发条件
            contingent_condition = order["ContingentCondition"]

            # 报单立即有效
            if contingent_condition == "Immediately":
                # 立刻撮合
                self.__cross_order(strategy_id, order_ref, direction, last_price, order)
            # 止损单
            elif contingent_condition == "Touch":
                if stop_price is None:
                    self.__handler_waste_order(strategy_id, order_ref, order)
                elif (last_price >= stop_price and direction == "Buy") or (last_price <= stop_price and direction == "Sell"):
                    self.__cross_order(strategy_id, order_ref, direction, last_price, order)
            # 止盈单
            elif contingent_condition == "TouchProfit":
                if stop_price is None:
                    self.__handler_waste_order(strategy_id, order_ref, order)
                elif (last_price <= stop_price and direction == "Buy") or (last_price >= stop_price and direction == "Sell"):
                    self.__cross_order(strategy_id, order_ref, direction, last_price, order)
            # 预埋单
            elif contingent_condition == "ParkedOrder":
                # 预埋单需要开始后进行处理，但是有行情就表示开市，直接撮合
                self.__cross_order(strategy_id, order_ref, direction, last_price, order)
            # 不符合协议逻辑，直接转为废单
            else:
                self.__handler_waste_order(strategy_id, order_ref, order)
            
    def __cross_order(self, strategy_id: str, order_ref: str, direction: str, last_price: float, order: dict):
        """撮合订单"""
        # 提取订单报价
        order_price = order["LimitPrice"]

        # 判断订单类型
        order_type = order["OrderPriceType"]

        # 市价单
        if order_type == "Any":
            self.__handler_done_order(
                strategy_id, 
                order_ref, 
                last_price
            )
        # 最新价单
        elif order_type == "Last":
            self.__handler_done_order(
                strategy_id, 
                order_ref, 
                last_price
            )
        # 限价单
        elif order_type == "Limit":
            if (last_price <= order_price and direction == "Buy") or (last_price >= order_price and direction == "Sell"):
                self.__handler_done_order(
                    strategy_id, 
                    order_ref, 
                    last_price
                )
        # 最优价单
        elif order_type == "Best":
            # 获取对手方的第一个价格
            snapshot_df = self.last_snapshot()
            symbol_snapshot_df = snapshot_df[snapshot_df["InstrumentID"] == instrument_id]
            opponent_price = symbol_snapshot_df["BidPrice1" if direction == "Buy" else "AskPrice1"].iloc[-1]

            self.__handler_done_order(
                strategy_id, 
                order_ref, 
                opponent_price
            )
        # 非法报单
        else:
            # 废单处理
            self.__handler_waste_order(strategy_id, order_ref, order)

    def __handler_done_order(self, strategy_id: str, order_ref: str, order_price: float):
        """记录成交"""
        # 提取订单
        order = self.__insert_order_table[(strategy_id, order_ref)]

        # 直接撮成功，并推送
        order['OrderSubmitStatus'] = 'Accepted'
        order['OrderStatus'] = 'AllTraded'
        self.strategy_registration_table()[strategy_id].on_order(order)
        
        # 创建一个交易记录
        date = self.last_quote_date()
        trade_record = {
            "Date": date,
            "Datetime": self.last_quote_datetime(),
            "StrategyID": strategy_id,
            "TradeRecordID": self.__trade_record_id,
            "InstrumentID": order["InstrumentID"],
            "ExchangeID": order["ExchangeID"],
            "Direction": order["Direction"],
            "Offset": order["CombOffsetFlag"],
            "Price": order_price,
            "Volume": order["VolumeTotalOriginal"],
            "OrderRef": order_ref,
        }

        # 记录每一笔交易
        self.__trade_record_table.append(trade_record)

        # 记录id自增
        self.__trade_record_id += 1

        # 撮合成功，删除订单
        del self.__insert_order_table[(strategy_id, order_ref)]

    def __clear_waste_order(self):
        """清理废单"""
        # 最新时间
        last_datetime = self.last_quote_datetime()
        year, month, day = last_datetime.year, last_datetime.month, last_datetime.day

        # 遍历所有订单，查阅触发条件
        for strategy_id, order_ref in list(self.__insert_order_table.keys()):
            # 提取订单有效期类型
            order = self.__insert_order_table[(strategy_id, order_ref)]
            insert_datetime = order['InsertDateTime']
            time_condition = order['TimeCondition']
            
            # 立即完成
            if time_condition == "IOC":
                # 没有成交立即撤单
                pass
            # 本节有效
            elif time_condition == "GFS":
                if ((datetime(year, month, day, 9, 0, 0, 0) <= last_datetime.day <= datetime(year, month, day, 10, 30, 0, 0) and 
                     datetime(year, month, day, 9, 0, 0, 0) <= insert_datetime <= datetime(year, month, day, 10, 30, 0, 0)) or 
                    (datetime(year, month, day, 10, 30, 0, 0) <= last_datetime.day <= datetime(year, month, day, 11, 30, 0, 0) and 
                     datetime(year, month, day, 10, 30, 0, 0) <= insert_datetime <= datetime(year, month, day, 11, 30, 0, 0)) or 
                    (datetime(year, month, day, 13, 30, 0, 0) <= last_datetime.day <= datetime(year, month, day, 15, 00, 0, 0) and 
                     datetime(year, month, day, 13, 30, 0, 0) <= insert_datetime <= datetime(year, month, day, 15, 00, 0, 0)) or
                    (datetime(year, month, day, 21, 00, 0, 0) <= last_datetime.day <= datetime(year, month, day+1, 1, 00, 0, 0) and 
                     datetime(year, month, day, 21, 00, 0, 0) <= insert_datetime <= datetime(year, month, day+1, 1, 00, 0, 0))):
                    continue
            # 当日有效
            elif time_condition == "GFD":
                if last_datetime.day <= insert_datetime.day:
                    continue
            # 指定日期前有效
            elif time_condition == "GTD":
                gtd_date = order.get('InsertDateTime', None)
                if gtd_date is not None:
                    gtd_date = datetime.strptime(gtd_date, "%Y%m%d")
                    if gtd_date >= last_datetime:
                        continue
            # 撤销前有效
            elif time_condition == "GTC":
                continue
            # 集合竞价有效
            elif time_condition == "GFA":
                if datetime(year, month, day, 8, 55, 0, 0) <= last_datetime <= datetime(year, month, day, 9, 0, 0, 0):
                    continue
            # 啥都不是，废单
            else:
                pass

            # 处理废单
            self.__handler_waste_order(strategy_id, order_ref, order)

    def __handler_waste_order(self, strategy_id: str, order_ref: str, order: dict):
        """执行废单处理"""
        # 处理废单
        order["OrderSubmitStatus"] = "InsertRejected"
        order["OrderStatus"] = "Canceled"
        del self.__insert_order_table[(strategy_id, order_ref)]
        self.strategy_registration_table()[strategy_id].on_order(order)

    def __calculate_daily_result(self):
        """计算逐日盯市结果"""
        # 没有交易数据不做计算
        if 0 == len(self.__trade_record_table):
            return

        # 将所有交易记录处理为一个dataframe，加速后续计算
        self.__trade_record_df = pd.DataFrame(self.__trade_record_table)

        # 安装不同的策略，日期，交易标的分组，计算净收益
        self.__trade_record_df.groupby(["StrategyID", "Date", "InstrumentID"]).apply(
            self.__calculate_daily_position_change
        )

        # 将每日计算结果由字段转换为一个dataframe
        self.__daily_result_df = pd.DataFrame(self.__daily_result_table)

        # 计算每日起始仓位和结束
        self.__daily_result_df["EndPosition"] = self.__daily_result_df["PositionChange"].cumsum()
        self.__daily_result_df["StartPosition"] = self.__daily_result_df["EndPosition"] - self.__daily_result_df["PositionChange"]
        
        # 计算换手
        self.__daily_result_df["Turnover"] = self.__daily_result_df.apply(
            self.__calculate_daily_turnover, 
            axis=1
        )
        
        # 计算佣金
        self.__daily_result_df["Commission"] = self.__daily_result_df["Turnover"] * self.__rate

        # 计算滑点
        self.__daily_result_df["Slippage"] = self.__daily_result_df.apply(
            lambda x: x["Volume"] * self.__slippage * self.__size, 
            axis=1
        )

        # 计算持仓收益
        self.__daily_result_df["HoldingPnl"] = self.__daily_result_df.apply(
            lambda x: x["StartPosition"] * (x["ClosePrice"] - x["PreClosePrice"]) * self.__size, 
            axis=1
        )

        # 计算交易收益
        self.__daily_result_df["TradingPnl"] = self.__daily_result_df.apply(
            self.__calculate_trading_pnl_turnover, 
            axis=1
        )

        # 计算总收益
        self.__daily_result_df["TotalPnl"] = self.__daily_result_df["TradingPnl"] + self.__daily_result_df["HoldingPnl"]

        # 计算净收益
        self.__daily_result_df["NetPnl"] = self.__daily_result_df["TotalPnl"] - self.__daily_result_df["Commission"] - self.__daily_result_df["Slippage"]

    def __calculate_backtest_statistics_result(self):
        """计算整个回测的数据统计结果"""
        if self.__daily_result_df is None or self.__daily_result_df.empty:
            return
        self.__daily_result_df = self.__daily_result_df.groupby([
            "StrategyID", "InstrumentID"
        ]).apply(
            self.__calculate_backtest_group_statistics_result
        )

    def __calculate_backtest_group_statistics_result(self, daily_result_df: pd.DataFrame):
        """计算整个不同策略在不同标的上回测的数据统计结果"""
        # 获取分组信息
        strategy_id = daily_result_df["StrategyID"].iloc[0]
        instrument_id = daily_result_df["InstrumentID"].iloc[0]

        # 计算一些需要的中间数据 
        daily_result_df["Balance"] = daily_result_df["NetPnl"].cumsum() + self.__capital
        daily_result_df["HighLevel"] = (
            daily_result_df["Balance"].rolling(
                min_periods=1, 
                window=len(daily_result_df), 
                center=False
            ).max()
        )
        pre_balance = daily_result_df["Balance"].shift(1)
        pre_balance.iloc[0] = self.__capital
        x = daily_result_df["Balance"] / pre_balance
        x[x <= 0] = np.nan
        daily_result_df["Return"] = np.log(x).fillna(0)
        daily_result_df["DrawDown"] = daily_result_df["Balance"] - daily_result_df["HighLevel"]
        daily_result_df["Ddpercent"] = daily_result_df["DrawDown"] / daily_result_df["HighLevel"] * 100
        
        # 计算数值回测的数据时间段
        start_date = daily_result_df["Date"].min()
        end_date = daily_result_df["Date"].max()
        total_days = daily_result_df.shape[0]

        # 获取收益天数，遭受损失天数
        profit_days = daily_result_df[daily_result_df["NetPnl"] > 0].shape[0]
        loss_days = daily_result_df[daily_result_df["NetPnl"] < 0].shape[0]

        # 最总资金，总收益率
        end_balance = daily_result_df["Balance"].iloc[-1]
        total_return = (end_balance / self.__capital - 1) * 100

        # 最大回撤，百分比最大回撤
        max_drawdown = daily_result_df["DrawDown"].min()
        max_ddpercent = daily_result_df["Ddpercent"].min()

        # # 最长回撤天数
        max_drawdown_end_index = daily_result_df["DrawDown"].idxmin()
        max_balance = daily_result_df[:(max_drawdown_end_index if max_drawdown_end_index > 0 else 1)]["Balance"].max()
        max_drawdown_start = daily_result_df[daily_result_df["Balance"] == max_balance]["Date"].iloc[0].to_pydatetime()
        max_drawdown_end = daily_result_df[daily_result_df["DrawDown"] == max_drawdown]["Date"].iloc[0].to_pydatetime()
        max_drawdown_duration = (max_drawdown_end - max_drawdown_start).days

        # 总盈亏/日均盈亏
        total_net_pnl = daily_result_df["NetPnl"].sum()
        daily_net_pnl = total_net_pnl / total_days

        # 总手续费/日均手续费
        total_commission = daily_result_df["Commission"].sum()
        daily_commission = total_commission / total_days

        # 总滑点/日均滑点
        total_slippage = daily_result_df["Slippage"].sum()
        daily_slippage = total_slippage / total_days

        # 总成交金额/日均成交金额
        total_turnover = daily_result_df["Turnover"].sum()
        daily_turnover = total_turnover / total_days

        # 总成交笔数/日均成交笔数/年化收益/
        total_trade_count = daily_result_df["TradeCount"].sum()
        daily_trade_count = total_trade_count / total_days

        # 总收益率/日均收益率
        total_return = (end_balance / self.__capital - 1) * 100
        daily_return = daily_result_df["Return"].mean() * 100
        annual_return = total_return / total_days * self.__annual_days
        return_std = daily_result_df["Return"].std() * 100

        # 夏普比率
        sharpe_ratio = 0
        if return_std:
            daily_risk_free = self.__risk_free / np.sqrt(self.__annual_days)
            sharpe_ratio = (daily_return - daily_risk_free) / return_std * np.sqrt(self.__annual_days)    

        # 收益回撤比
        return_drawdown_ratio = -total_return / max_ddpercent

        # 统计计算/收益标准差
        if strategy_id not in self.__backtest_statistics_result:
            self.__backtest_statistics_result[strategy_id] = {}
        self.__backtest_statistics_result[strategy_id][instrument_id] = {
            "StartDate": start_date,                                                     # 首个交易日
            "EndDate": end_date,                                                         # 最后交易日
            "TotalDays": total_days,                                                     # 总交易日
            "ProfitDays": profit_days,                                                   # 盈利交易日
            "LossDays": loss_days,                                                       # 亏损交易日
            "Capital": self.__capital,                                                   # 起始资金
            "EndBalance": round(end_balance, 2),                                         # 结束资金
            "TotalReturn": round(total_return, 2),                                       # 总收益率
            "AnnualReturn": round(total_return / total_days * self.__annual_days, 2),    # 年化收益
            "MaxDrawdown": round(max_drawdown, 2),                                       # 最大回撤
            "MaxDdpercent": round(max_ddpercent, 2),                                     # 百分比最大回撤
            "MaxDrawdownDuration": max_drawdown_duration,                                # 最长回撤天数
            "TotalNetPnl": round(total_net_pnl, 2),                                      # 总盈亏
            "TotalCommission": round(total_commission, 2),                               # 总手续费
            "TotalSlippage": total_slippage,                                             # 总滑点
            "TotalTurnover": total_turnover,                                             # 总成交金额
            "TotalTradeCount": total_trade_count,                                        # 总成交笔数
            "DailyNetPnl": round(daily_net_pnl, 2),                                      # 日均盈亏
            "DailyCommission": round(daily_commission, 2),                               # 日均手续费
            "DailySlippage": daily_slippage,                                             # 日均滑点
            "DailyTurnover": round(daily_turnover, 2),                                   # 日均成交金额
            "DailyTrade_count": daily_trade_count,                                       # 日均成交笔数
            "DailyReturn": round(daily_return, 2),                                       # 日均收益率
            "ReturnStd": round(return_std, 2),                                           # 收益标准差
            "SharpeRatio": round(sharpe_ratio, 2),                                       # 夏普比率
            "ReturnDrawdownRatio": round(return_drawdown_ratio, 2),                      # 收益回撤比
        }
        df = pd.DataFrame([self.__backtest_statistics_result[strategy_id][instrument_id]])
        df.insert(loc=0, column="StrategyID", value=strategy_id)
        df.insert(loc=1, column="InstrumentID", value=instrument_id)
        self.__backtest_statistics_result_df = df if self.__backtest_statistics_result_df is None else pd.concat([self.__backtest_statistics_result_df, df])

        # 计算的一些中间变量返回给逐日盯视记录
        return daily_result_df

    def __calculate_daily_position_change(self, trade_record_df: pd.DataFrame):
        """计算每日某一只标的的持仓变化"""
        # 获取日期和标的，便于记录数据
        strategy_id = trade_record_df["StrategyID"].iloc[0]
        date = trade_record_df["Date"].iloc[0].to_pydatetime()
        instrument_id = trade_record_df["InstrumentID"].iloc[0]

        # 计算仓位变化
        trade_record_df["PositionChange"] = trade_record_df.apply(lambda x: x["Volume"] if x["Direction"]=="Buy" else -x["Volume"], axis=1)
        position_change = trade_record_df["PositionChange"].sum()
        volume = trade_record_df["Volume"].sum()

        self.__daily_result_table.append({
            "PreClosePrice": self.__daily_close_table[date][instrument_id]["PreClosePrice"],
            "ClosePrice": self.__daily_close_table[date][instrument_id]["ClosePrice"],
            "StrategyID": strategy_id,
            "Date": date,
            "InstrumentID": instrument_id,
            "PositionChange": position_change,
            "Volume": volume,
            "TradeCount": trade_record_df.shape[0],
        })

    def __calculate_daily_turnover(self, daily_record: pd.Series):
        """计算每日换手"""
        # 交易数据分类检索条件
        date = daily_record["Date"]
        strategy_id = daily_record["StrategyID"]
        instrument_id = daily_record["InstrumentID"]

        # 检索交易数据
        trade_record_df = self.__trade_record_df[
            (self.__trade_record_df["Date"] == date) & 
            (self.__trade_record_df["StrategyID"] == strategy_id) & 
            (self.__trade_record_df["InstrumentID"] == instrument_id)
        ]

        # 计算当日换手
        trade_record_df["Turnover"] = trade_record_df["Volume"] * trade_record_df["Price"] * self.__size
        return trade_record_df["Turnover"].sum()

    def __calculate_trading_pnl_turnover(self, daily_record: pd.Series):
        """计算每日换手"""
        # 交易数据分类检索条件
        date = daily_record["Date"]
        strategy_id = daily_record["StrategyID"]
        instrument_id = daily_record["InstrumentID"]
        
        # 计算用数据
        close_price = daily_record["ClosePrice"]

        # 检索交易数据
        trade_record_df = self.__trade_record_df[
            (self.__trade_record_df["Date"] == date) & 
            (self.__trade_record_df["StrategyID"] == strategy_id) & 
            (self.__trade_record_df["InstrumentID"] == instrument_id)
        ].sort_values(["Datetime"])

        # 计算当日成交收益
        trade_record_df["TradingPnl"] = trade_record_df.apply(
            lambda x: x["Volume"] * (1 if x["Direction"] == "Buy" else -1) * (close_price - x["Price"]) * self.__size,
            axis=1
        )
        return round(trade_record_df["TradingPnl"].sum(), 2)
