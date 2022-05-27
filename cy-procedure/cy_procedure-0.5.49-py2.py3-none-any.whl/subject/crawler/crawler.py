import pytz
import time
from multiprocessing.pool import Pool
from cy_data_access.util.convert import *
from cy_data_access.models.market import *
from cy_widgets.fetcher.exchange import *
from cy_components.helpers.formatter import *
from .config_reader import *
from ...generic.spot_fetching import *


class CandleRealtimeCrawler:
    """
    1. 从 ConfigReader 获取需要抓取的相关配置
    2. 检查完整，补齐
    3. 等待到下一分钟开始
    4. 并发开始抓取
    """

    __config_reader: CrawlerConfigReader

    def __init__(self, config_reader, limit=10, duration=1, tolerance=2, start_second=47):
        self.__config_reader = config_reader
        self.__limit = limit
        self.__duration = duration  # 两次间隔
        self.__tolerance = tolerance  # 少几根不通过
        self.__start_second = start_second  # 任务开始的秒数

    def __get_configs(self):
        """获取需要抓取的K线配置"""
        return self.__config_reader.configs

    def fetch_kline_and_save(self, config: CrawlerItemConfig):
        """抓取"""
        start_time = datetime.now().astimezone(tz=pytz.utc)
        time_frame = config.time_frame
        coin_pair = config.coin_pair
        for _ in range(5):  # 5 次，不行就算了
            try:
                df = ExchangeFetcher(self.__config_reader.ccxt_provider).fetch_real_time_candle_data(coin_pair, time_frame, self.__limit)

                # 空的
                if df.empty:
                    continue

                # 排序
                df = df.sort_values(COL_CANDLE_BEGIN_TIME)

                # 计算 delta
                delta = start_time - df.iloc[-1].candle_begin_time

                # print(coin_pair.formatted(), df.shape[0], delta.total_seconds())
                # print(df[-1:])
                if time_frame.value.endswith('m'):
                    has_last = delta.total_seconds() < int(time_frame.value[:-1]) * 60 * self.__tolerance
                elif time_frame.value.endswith('h'):
                    has_last = delta.total_seconds() < int(time_frame.value[:-1]) * 60 * 60 * self.__tolerance
                else:
                    print('time_interval不以m或者h结尾，出错，程序exit')
                    exit()

                if not has_last:
                    print('{} {} 获取数据不包含最新的数据，重新获取'.format(config.coin_pair.formatted(), config.time_frame.value))
                    time.sleep(1)
                    continue

                json_list = convert_df_to_json_list(df, COL_CANDLE_BEGIN_TIME)
                candle_record_class_with_components(config.exchange_name, config.coin_pair, config.time_frame, config.coin_tail).bulk_upsert_records(json_list)
                return
            except Exception as e:
                print('{} {} 出错'.format(config.coin_pair.formatted(), config.time_frame.value))
                print(e)
                time.sleep(5)

    def __dispatch_task(self, configs):
        """分配任务"""
        try:
            start = time.time()
            pool = Pool(processes=2)
            _ = pool.map(self.fetch_kline_and_save, configs)
        finally:
            pool.close()
            pool.join()
            print('抓取任务用时: ', time.time() - start, '结束时间:', datetime.now())

    def run_crawling(self):
        configs = self.__get_configs()
        self.__dispatch_task(configs)
        while True:
            # 等待到下一次
            current_time = datetime.now().astimezone(tz=pytz.utc)
            if current_time.second < self.__start_second - 5:
                next_time = current_time.replace(second=self.__start_second)
            else:
                next_time = current_time.replace(second=self.__start_second) + timedelta(minutes=self.__duration)
            print('下次', self.__config_reader.name, next_time)
            time.sleep(max(0, (next_time - datetime.now().astimezone(tz=pytz.utc)).seconds))
            while True:  # 在靠近目标时间时
                if datetime.now().astimezone(tz=pytz.utc) > next_time:
                    break
            configs = self.__get_configs()
            self.__dispatch_task(configs)
