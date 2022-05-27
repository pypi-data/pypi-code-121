#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import sys

sys.path.insert(1, "./model")
sys.path.insert(2, "./interface")
sys.path.insert(3, "./libs")
from com.interface.mdc_gateway_base_define import EMarketDataType, ESecurityIDSource, ESecurityType, \
    ESubscribeActionType, MDPlaybackExrightsType, GateWayServerConfig, QueryServerConfig
import com.insight.common
import com.insight.query
import com.insight.playback
import com.insight.subscribe


def onSubscribe_MD_TICK_StockType(mdStock):
    print(mdStock)


# 登陆
def login():
    # 登陆前 初始化
    uatuser = "USER016189SIT001"
    uatpassword = "123!@#qweQWE"
    user = "USER016189TMN01"
    password = "User016189"
    result = com.insight.common.login(user, password)
    print(result)


# 根据证券数据来源订阅行情数据,由三部分确定行情数据
# 行情源(SecurityIdSource):XSHG(沪市)|XSHE(深市)|...
# 证券类型(SecurityType):BondType(债)|StockType(股)|FundType(基)|IndexType(指)|OptionType(期权)|...
# 数据类型(MarketDataTypes):MD_TICK(快照)|MD_TRANSACTION(逐笔成交)|MD_ORDER(逐笔委托)|...
def subscribe_by_type():
    # element
    # params1: ESecurityIDSource枚举值 --行情源
    # params2: ESecurityType的枚举值 --证券类型
    # params3: EMarketDataType的枚举值集合 --数据类型
    datatype = ESubscribeActionType.COVERAGE
    marketdatatypes = {"ESecurityIDSource": ESecurityIDSource.XSHG, "ESecurityType": ESecurityType.StockType,
                       "EMarketDataType": EMarketDataType.MD_TICK}
    com.insight.subscribe.subscribe_by_type(marketdatatypes, datatype)


# 根据证券ID来源订阅行情数据
def subscribe_by_id():
    datatype = ESubscribeActionType.COVERAGE
    HTSCSecurityID = {"HTSCSecurityID": "002371.SZ", "ESecurityType": ESecurityType.StockType,
                      "EMarketDataType": EMarketDataType.MD_TICK}
    com.insight.subscribe.subscribe_by_id(HTSCSecurityID, datatype)


def query_fin_info():
    query_type = 1102010003
    params = {"HTSC_SECURITY_ID": "510050.SH", "START_DATE": "20210101", "END_DATE": "20210107"}
    result = com.insight.query.query_fin_info(query_type, params)
    if isinstance(result, list):
        for response in iter(result):
            print(response)
    else:
        print(result)


# 查询历史上所有的指定证券的基础信息 -- 在data_handle.py 数据回调接口OnMarketData()中marketdata.marketDataType = MD_CONSTANT
# params:securityIdSource 为市场ESecurityIDSource 枚举值;securityType 为 ESecurityType枚举值
def query_mdcontant_type():
    # params:security_idsource 为 ESecurityIDSource枚举值
    # params:security_type 为 ESecurityType枚举值
    # 沪市 股票
    security_idsource = ESecurityIDSource.XSHG
    security_type = ESecurityType.StockType
    idsource_and_type = {"ESecurityIDSource": security_idsource, "ESecurityType": security_type}
    com.insight.query.query_basicInfo_by_type(idsource_and_type, False)


# 查询今日最新的指定证券的基础信息 -- 在data_handle.py 数据回调接口OnMarketData()中marketdata.marketDataType = MD_CONSTANT
# params:securityIdSource 为市场ESecurityIDSource 枚举值;securityType 为 ESecurityType枚举值
def query_last_mdcontant_type():
    # 按市场查询
    # 沪市 股票

    security_idsource = ESecurityIDSource.XSHG
    security_type = ESecurityType.StockType
    idsource_and_type = {"ESecurityIDSource": security_idsource, "ESecurityType": security_type}
    com.insight.query.query_basicInfo_by_type(idsource_and_type, True)


# 查询历史上所有的指定证券的基础信息 -- 在data_handle.py 数据回调接口OnMarketData()中marketdata.marketDataType = MD_CONSTANT
# params:securityIdSource 为市场ESecurityIDSource 枚举值;securityType 为 ESecurityType枚举值
def query_mdcontant_id():
    # params:security_idsource 为 ESecurityIDSource枚举值
    # params:security_type 为 ESecurityType枚举值
    # params:security_id_list 为 标的集合
    security_id_list = ["601688.SH"]  # 置空表示不额外查询某些标的
    com.insight.query.query_basicInfo_by_id(security_id_list, False)


# 查询今日最新的指定证券的基础信息 -- 在data_handle.py 数据回调接口OnMarketData()中marketdata.marketDataType = MD_CONSTANT
# params:securityIdSource 为市场ESecurityIDSource 枚举值;securityType 为 ESecurityType枚举值
def query_last_mdcontant_id():
    # 按市场查询
    # 沪市 股票

    # params:security_id_list 为 标的集合
    security_id_list = ["601688.SH"]  # 置空表示不额外查询某些标的
    com.insight.query.query_basicInfo_by_id(security_id_list, True)


# 查询指定证券的ETF的基础信息 -- 在data_handle.py 数据回调接口OnMarketData()中marketdata.marketDataType = MD_ETF_BASICINFO
# params:securityIdSource 为市场ESecurityIDSource 枚举值;securityType 为 ESecurityType枚举值
def query_ETFinfo():
    # params:securityIDSource 为 ESecurityIDSource枚举值
    # params:securityType 为 ESecurityType枚举值
    com.insight.query.query_ETFinfo(ESecurityIDSource.XSHG, ESecurityType.FundType)


# 查询指定证券的最新一条Tick数据 -- 在data_handle.py 数据回调接口OnMarketData()中marketdata.marketDataType = MD_TICK
# params:securityIdSource 为市场ESecurityIDSource 枚举值;securityType 为 ESecurityType枚举值
def query_last_mdtick():
    # params:security_idsource 为 ESecurityIDSource枚举值
    # params:security_type 为 ESecurityType枚举值
    # 沪市 股票
    com.insight.query.query_last_tick_by_type(ESecurityIDSource.XSHG, ESecurityType.StockType)


# 回放接口 (注意：securitylist 和 securityIdList取并集!!!)
# 回放限制
# 对于回放而言，时间限制由股票只数和天数的乘积决定，要求 回放只数 × 回放天数 × 证券权重 ≤ 450，交易时间段内回放功能 乘积<=200。
# Tick/Transaction/Order回放时间范围限制是30天，每支证券权重为1，即可以回放15只股票30天以内的数据或450支股票1天内数据。
# 日K数据回放时间范围限制是365天，每支证券权重为0.005。
# 分钟K线数据回放时间范围限制是90天，每支证券权重0.05。
# 数据最早可以回放到 2017年1月2日
def play_back():
    # 回放数据类型 EMarketDataType 详情请参阅 数据手册EMarketDataType
    # 示例：MD_TICK
    marketdata_type = EMarketDataType.MD_TICK

    # 是否复权 EPlaybackTaskStatus 详情请参阅 数据手册EPlaybackTaskStatus
    # 示例： 不复权
    exrights_type = MDPlaybackExrightsType.DEFAULT_EXRIGHTS_TYPE

    # 回放时间起：start_time 注意格式
    # 回放时间止：stop_time  注意格式
    # 回放时间起止间隔 不超过上述 时间范围限制
    start_time = "20220420090000"
    stop_time = "20220420150000"

    # security_id_list 为回放 标的列表,不需要使用请置空
    security_id_list = ["601688.SH", "000014.SZ"]

    # 特别注意！！！！
    # security_id_list 注意回放限制
    com.insight.playback.playback(security_id_list, marketdata_type, exrights_type, start_time, stop_time)


# 盘中回放接口 --securitylist 和 securityIdList取并集
# Can only query data for one day
def play_back_oneday():
    # 回放数据类型 EMarketDataType 详情请参阅 数据手册EMarketDataType
    # 示例：MD_TICK
    marketdata_type = EMarketDataType.MD_TICK

    # 是否复权 EPlaybackTaskStatus 详情请参阅 数据手册EPlaybackTaskStatus
    # 示例： 不复权
    exrights_type = MDPlaybackExrightsType.DEFAULT_EXRIGHTS_TYPE

    # 是否按照mdtime排序
    isMdtime = True

    # security_id_list 为回放 标的列表,不需要使用请置空
    security_id_list = ["601688.SH", "000014.SZ"]

    # 特别注意！！！！
    # security_id_list 注意回放限制
    com.insight.playback.play_back_oneday(security_id_list, marketdata_type, exrights_type, isMdtime)


# 获取当前版本号
def get_version():
    print(com.insight.common.get_version())


# 释放资源
def fini():
    com.insight.common.fini()


# 使用指导：登陆 -> 订阅/查询/回放 -> 退出
def main():
    # 登陆部分调用
    get_version()
    login()
    # 订阅部分接口调用
    # query_fin_info()
    subscribe_by_type()
    # subscribe_by_id()
    # 查询部分接口调用
    # query_mdcontant_type()
    # query_last_mdcontant_type()
    # query_mdcontant_id()
    # query_last_mdcontant_id()
    # query_ETFinfo()
    # query_last_mdtick()
    # 回放部分接口调用
    # play_back()
    # play_back_oneday()
    # 退出释放资源
    fini()


if __name__ == "__main__":
    # insight SDK 采用网络异步方式 ---- 请求访问和数据返回 异步交互
    # 这里是 functional_test.py 是 登陆、订阅、查询、回测（也称回放）操作部分
    # 以订阅为例： functional_test.py 中，执行登陆->订阅,操作结束后,数据通过 data_handle.py中 OnRecvMarkertData()的成员方法回调返回（回调详情请参照使用手册）
    main()
