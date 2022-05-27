from datetime import datetime, timedelta


class kline_level:
    minute=0
    day=1


class generator:
    """1分钟k线生成器"""

    def __init__(self, call_back_function=None):
        """初始化方法"""

        # 记录计算参数
        self.__call_back_function = call_back_function               # 新的一根k线创建之后的回调函数

        # 计算的各个容器
        self.__kline_cache = dict()                                  # K线的缓存容器{标的，K线数据}     

    def update_tick(self, tick: dict):
        """更新tick数据"""

        # 容错，如果回调函数对象是None，无需处理
        if self.__call_back_function is None:
            return

        # 解析行情
        date = tick.get("Date", None)
        time = tick.get("Time", None)
        millisecond = tick.get("Millisecond", 0) * 1000
        instrument_id = tick.get("InstrumentID", None)

        last = tick.get("Last", None)
        volume = tick.get("Volume", None)
        amount = tick.get("Amount", None)

        # 如果解析失败，退出
        if last is None or date is None or time is None or instrument_id is None:
            return

        # 将时间转换为datetime，方便计算
        current_datetime = datetime.strptime(
            f"{date} {time}.{millisecond}", "%Y%m%d %H:%M:%S.%f"
        )

        # 需要计算的kline时间
        kline_datetime = datetime(
            current_datetime.year,
            current_datetime.month,
            current_datetime.day,
            current_datetime.hour,
            current_datetime.minute,
            0, 0
        ) + timedelta(minutes=1)

        # 如果触发事件没有设置过，利用第一帧配置
        if instrument_id not in self.__kline_cache:
            self.__kline_cache[instrument_id] = {
                "InstrumentID": instrument_id,
                "DateTime": kline_datetime,
                "Date": date,
                "Time": time,
                "OpenPrice": last,
                "HighPrice": last,
                "LowPrice": last,
                "ClosePrice": last,
                "Volume": volume,
                "Amount": amount,
            }
            return

        # 如果k线的计算时间发生改变，触发回调，将K线推送出去
        if kline_datetime != self.__kline_cache[instrument_id]["DateTime"]:
            # 触发回调推送K线
            self.__call_back_function(
                self.__kline_cache[instrument_id]
            )

            # 重新填充缓存数据
            self.__kline_cache[instrument_id] = {
                "InstrumentID": instrument_id,
                "DateTime": kline_datetime,
                "Date": date,
                "Time": time,
                "OpenPrice": last,
                "HighPrice": last,
                "LowPrice": last,
                "ClosePrice": last,
                "Volume": volume,
                "Amount": amount,
            }
            return

        # 上述情况都不符合，进行计算
        self.__kline_cache[instrument_id]["HighPrice"] = max(last, self.__kline_cache[instrument_id]["HighPrice"])
        self.__kline_cache[instrument_id]["LowPrice"] = min(last, self.__kline_cache[instrument_id]["LowPrice"])
        self.__kline_cache[instrument_id]["ClosePrice"] = last
        self.__kline_cache[instrument_id]["Volume"] = volume
        self.__kline_cache[instrument_id]["Amount"] = amount


class synthesizer:
    """高等K线合成器"""

    def __init__(
        self, 
        intreval: int = 1, 
        level: kline_level = kline_level.minute, 
        call_back_function = None
    ):
        """初始化方法"""

        # 参数容错
        assert intreval > 0, f"高等K线合成迭代时间间隔值，必须大于0"

        # 记录参数
        self.__level = level 
        self.__intreval = intreval 
        self.__call_back_function = call_back_function

        # K线的缓存容器{标的，[K线数据列表]}
        self.__kline_cache = dict()

    def update_kline(self, kline: dict):
        """更新1分钟K线数据"""

        # 容错，如果回调函数对象是None，无需处理
        if self.__call_back_function is None:
            return

        # 将新的K线缓存
        instrument_id = kline["InstrumentID"]
        if instrument_id not in self.__kline_cache:
            self.__kline_cache[instrument_id] = list()
        self.__kline_cache[instrument_id].append(kline)

        # 判断需要合成的高等K线级别，选择处理方式
        if self.__level == kline_level.minute:
            self.__synthesize_minute_kline(instrument_id)
        elif self.__level == kline_level.day:
            self.__synthesize_day_kline(instrument_id)
        else:
            return

    def __synthesize_minute_kline(self, instrument_id: str):
        """合成分钟K线"""

        # 查询缓存
        kline_list = self.__kline_cache[instrument_id]

        # 容错，如果还是计算1分钟k线，无需计算，直接推送
        if 1 == self.__intreval:
            self.__call_back_function(kline[0])
            return

        # 判断是否触发计算(如果缓存中没有数据，无需计算，只需要对新的K线做缓存)
        delta_datetime = kline_list[-1]["DateTime"] - kline_list[0]["DateTime"]
        delta_minutes = int(delta_datetime.seconds / 60)
        if delta_minutes >= (self.__intreval - 1):
            self.__synthesize_trigger(instrument_id)
        
    def __synthesize_day_kline(self, instrument_id: str):
        """合成日K线"""

        # 查询缓存
        kline_list = self.__kline_cache[instrument_id]

        # 判断是否触发计算(如果缓存中没有数据，无需计算，只需要对新的K线做缓存)
        delta_datetime = kline_list[-1]["DateTime"] - kline_list[0]["DateTime"]
        delta_days = delta_datetime.days
        if delta_days >= (self.__intreval - 1):
            self.__synthesize_trigger(instrument_id)

    def __synthesize_trigger(self, instrument_id: str):
        """合成触发器"""

        # 容错
        if instrument_id not in self.__kline_cache:
            return

        # 查询该标的K线缓存
        kline_list = self.__kline_cache[instrument_id]

        # 合成K线
        new_kline = {
            "InstrumentID": instrument_id,
            "DateTime": kline_list[-1]["DateTime"],
            "Date": kline_list[-1]["Date"],
            "Time": kline_list[-1]["Time"],
            "OpenPrice": kline_list[0]["OpenPrice"],
            "HighPrice": max([kline["HighPrice"] for kline in kline_list]),
            "LowPrice": min([kline["LowPrice"] for kline in kline_list]),
            "ClosePrice": kline_list[-1]["ClosePrice"],
            "Volume": kline_list[-1]["Volume"],
            "Amount": kline_list[-1]["Amount"],
        }

        # 推送
        self.__call_back_function(new_kline)

        # 清理缓存
        self.__kline_cache[instrument_id].clear()
