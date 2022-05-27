# -*- coding: utf-8 -*-

from collections import namedtuple
from enum import Enum


StrategyParameterTuple = namedtuple('StrategyParameterTuple', ['PORTFOLIO_NAME', 'PORTFOLIO_EN_NAME', 'OPEN_DATE', 'DELAY', 'REFRESH_DATE', 'CONSTRUCT_TYPE'])


class TimeDateFormat(Enum):
    YMDHYPHEN = '%Y-%m-%d'
    YMD = '%Y%m%d'
    YMDHMSHYPHEN = '%Y-%m-%d %H:%M:%S'
    YMDHMS = '%Y:%m:%d %H:%M:%S'
    Y = '%Y'
    HM = '%H:%M'
    YMDCN = '%Y年%m月%d日'
    YM = '%Y%m'
    MDHYPHEN = '%m-%d'
    YMDSLASH = '%Y/%m/%d'

class CovMethod(Enum):
    SAMPLECOV = 'SAMPLECOV'
    LEDOITWOLF = 'LEDOITWOLF'


class StyleFactors(Enum):
    BETA = 'BETA'
    MOMENTUM = 'MOMENTUM'
    SIZE = 'SIZE'
    EARNYILD = 'EARNYILD'
    RESVOL = 'RESVOL'
    GROWTH = 'GROWTH'
    BTOP = 'BTOP'
    LEVERAGE = 'LEVERAGE'
    LIQUIDTY = 'LIQUIDTY'
    SIZENL = 'SIZENL'


class IndustryFactors(Enum):
    Bank = ('Bank', '银行')
    RealEstate = ('RealEstate', '房地产')
    Health = ('Health', '生物医药')
    Transportation = ('Transportation', '交通运输')
    Mining = ('Mining', '采掘')
    NonFerMetal = ('NonFerMetal', '有色金属')
    HouseApp = ('HouseApp', '家用电器')
    LeiService = ('LeiService', '休闲服务')
    MachiEquip = ('MachiEquip', '机械设备')
    BuildDeco = ('BuildDeco', '建筑装饰')
    CommeTrade = ('CommeTrade', '商业贸易')
    CONMAT = ('CONMAT', '建筑材料')
    Auto = ('Auto', '汽车')
    Textile = ('Textile', '纺织服装')
    FoodBever = ('FoodBever', '食品饮料')
    Electronics = ('Electronics', '电子')
    Computer = ('computer', '计算机')
    LightIndus = ('LightIndus', '轻工制造')
    Utilities = ('Utilities', '公共事业')
    Telecom = ('Telecom', '通信')
    AgriForest = ('AgriForest', '农林牧渔')
    CHEM = ('CHEM', '化工')
    Media = ('Media', '传媒')
    IronSteel = ('IronSteel', '钢铁')
    NonBankFinan = ('NonBankFinan', '非银金融')
    ELECEQP = ('ELECEQP', '电气设备')
    AERODEF = ('AERODEF', '国防军工')
    Conglomerates = ('Conglomerates', '综合')


class Freq(Enum):
    DAY = 'DAY'
    MONTH = 'MONTH'
    WEEK = 'WEEK'


class ProcessType(Enum):
    BATCH = 'BATCH'
    ONLINE = 'ONLINE'

class HoldType(Enum):
    SHORT = 'SHORT'
    LONG = 'LONG'

class UploadType(Enum):
    FEEDS = 'FEEDS'
    STRATEGY = 'STRATEGY'

class StrategyParameters(Enum):
    ANALYSTADJ1 = StrategyParameterTuple(PORTFOLIO_NAME='王牌掘金一号策略', PORTFOLIO_EN_NAME='ANALYSTADJ1', OPEN_DATE='2017-01-01', DELAY=1, REFRESH_DATE=1, CONSTRUCT_TYPE='OPEN')





