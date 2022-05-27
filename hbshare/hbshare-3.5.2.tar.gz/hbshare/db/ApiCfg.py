from enum import Enum
from hbshare.base.upass import is_prod_env

# 办公环境
DOMAINS_OFFICE = {'hbcgi': 'data.howbuy.com', 's': 's.howbuy.com','ams':'ams-data.intelnal.howbuy.com'}
# 产线环境
DOMAINS_PROD = {'hbcgi': 'data.howbuy.com', 's': 's.howbuy.com','ams':'ams.inner.howbuy.com'}
P_TYPE = {'http': 'http://', 'ftp': 'ftp://', 'https': 'https://'}

class UrlCfg():
    def __init__(self, url, method,domain,parsePostDataFunc, parseParamsFunc, supportFields):
        self.__url__ = url
        self.method = method
        self.__domain__ = domain
        self.__parsePostDataFunc__ = parsePostDataFunc
        self.__parseParamsFunc__ = parseParamsFunc
        self.supportFields = supportFields

    def parsePostData(self, kwargs):
        return self.__parsePostDataFunc__(kwargs)

    def parseParams(self, kwargs):
        return self.__parseParamsFunc__(kwargs)

    def getUrl(self):
        if is_prod_env():
            return self.__url__ % DOMAINS_PROD.get(self.__domain__)
        return self.__url__ % DOMAINS_OFFICE.get(self.__domain__)

    def supportFields(self):
        return self.supportFields


class UrlEnum(Enum):

    @classmethod
    def getValue(self,name):
        '''根据枚举name匹配到枚举对象，并返回对应的value'''
        if name in self._member_names_:
            tmpEnum = self._member_map_[name]
            return tmpEnum.value
        else:
            raise ValueError("%s is not a valid UrlEnum" % name)

############################### 指数 ###############################
    # 查询指数行情
    MARKET_HQ = UrlCfg('http://%s/data/fund/brinson/zsjy','post', 'ams',
                       lambda x: {
                           'zqdm': x['zqdm'],
                           'jyrq': {
                               'startDate': x['startDate'],
                               'endDate': x['endDate']
                           },
                           'fields': x['fields'],
                           'page': x['page'],
                           'perPage': x['perPage']
                       },
                       lambda y: {},
                       supportFields=('jlzj', 'jyrq', 'scdm', 'zqdm', 'zqmc', 'qspj', 'kpjg', 'spjg', 'zgjg', 'zdjg', 'cjsl', 'cjjs',
                                      'cjbs', 'zdsl', 'zdfd', 'bdfd', 'hbjn', 'hb1z', 'hb4z', 'hb13z', 'hb26z', 'hb52z', 'hb1y', 'hb3y', 'hb6y',
                                      'hb1n', 'ggrq', 'recstat', 'checkflag', 'creator', 'modifier', 'checker', 'credt', 'moddt', 'stimestamp',
                                      'hb2n', 'hb3n', 'hb5n', 'hbdr', 'fl', 'pb', 'roe', 'gxl', 'pebfw', 'pbbfw', 'syl', 'nhsy1y', 'nhsy1n', 'nhsy2n',
                                      'nhsy3n', 'nhsy3y', 'nhsy6y', 'nhsy5n', 'gxlbfw', 'ltsz', 'zsz',)
                       )
    ''' 查询指数行情 '''

################################ 公募 ################################
    # 公募基金回报
    FUND_JJHB = UrlCfg('http://%s/data/fund/brinson/jjhb','post', 'ams',
                       lambda x: {
                           'jjdm': x['jjdm'],
                           'jzrq': {
                               'startDate': x['startDate'],
                               'endDate': x['endDate']
                           },
                           'fields': x['fields'],
                           'page': x['page'],
                           'perPage': x['perPage']
                       },
                       lambda y: {},
                       supportFields=('jzrq', 'jjdm', 'hbdr', 'hb1z', 'hb1y', 'hb2y', 'hb3y', 'hb4y', 'hb6y', 'hbjn', 'hb1n', 'hb2n',
                                      'hb3n', 'hb4n', 'hb5n', 'hbcl', 'hbfh', 'pm30r', 'pm60r', 'pm90r', 'pm180r', 'pmdr', 'pm1z', 'pm1y',
                                      'pm3y', 'pm6y', 'pmjn', 'pm1n', 'pm2n', 'pm3n', 'pm4n', 'pm5n', 'pmcl', 'qrsy', 'pm7r', 'wjsy',
                                      'recstat', 'checkflag', 'creator', 'modifier', 'checker', 'credt', 'moddt', 'stimestamp', 'hb2z',
                                      'hb3z', 'pm2z', 'pm3z', 'pmdr2', 'pm1z2', 'pm1y2', 'pm3y2', 'pm6y2', 'pmjn2', 'pm1n2', 'pm2n2', 'pm3n2',
                                      'pm4n2', 'pm5n2', 'pmcl2', 'pm2z2', 'pm3z2', 'nhsyl1y', 'nhsy3y', 'nhsy6y', 'nhsy12y', 'jbdl1y',
                                      'pmbzf1y', 'pmbzf3y', 'pmbzf1n', 'hmtjzs', 'sswx', 'xswx', 'nhsy14r', 'nhsy28r', 'nhsy30r', 'nhsy35r',
                                      'nhsy60r', 'nhsy90r', 'nhsy180r', 'nhsy1y', 'nhsy1n', 'nhsy2n', 'nhsy3n', 'nhsy5n', 'bfbpm3y', 'bfbpm6y',
                                      'bfbpm1n', 'bfbpm2n', 'bfbpm3n', 'bfbpm5n', 'bfbpmjn', 'bfbpm3y2', 'bfbpm6y2', 'bfbpm1n2', 'bfbpm3n2', 'zddr',)
                       )
    '''公募基金回报'''
    # 公募基金公募持仓数据
    FUND_JJ_GPZH = UrlCfg('http://%s/data/fund/brinson/gpzh' ,'post','ams',
                          lambda x: {
                              'jjdm': x['jjdm'],
                              'ggrq': {
                                  'startDate': x['startDate'],
                                  'endDate': x['endDate']
                              },
                              'fields': x['fields'],
                              'page': x['page'],
                              'perPage': x['perPage']
                          },
                          lambda y: {},
                          supportFields=('jjdm', 'qsrq', 'jsrq', 'zqdm', 'zqmc', 'ltms', 'tzlx', 'sszt', 'ccsz', 'ccsl',
                                         'zjbl', 'zgbl', 'zlbl', 'jzgj', 'jlfz', 'ggrq', 'recstat', 'checkflag',
                                         'creator', 'modifier', 'checker', 'credt', 'moddt', 'stimestamp', 'sftj',
                                         'szbdbl', 'slbdbl', 'zjblbdbl', 'zgblbd', 'zgblbdbl', 'zlblbdbl',)
                          )
    '''公募基金公募持仓数据'''
    # 公募持仓资产比例数据
    FUND_JJ_ZCPZ = UrlCfg('http://%s/data/fund/brinson/zcpz','post','ams',
                          lambda x: {
                              'jjdm': x['jjdm'],
                              'jsrq': {
                                  'startDate': x['startDate'],
                                  'endDate': x['endDate']
                              },
                              'fields': x['fields'],
                              'page': x['page'],
                              'perPage': x['perPage']
                          },
                          lambda y: {},
                          supportFields=('jjdm', 'jsrq', 'hbzl', 'jjzc', 'jzzc', 'zssz', 'jjsz', 'jjbl', 'gpbl',
                                         'qzsz', 'qzbl', 'zzsz', 'cqbl', 'kzbl', 'gzsz', 'gjbl', 'jzsz', 'jzbl',
                                         'ypsz', 'ypbl', 'qysz', 'qybl', 'qqsz', 'zqsz', 'zqbl', 'yhck', 'ckbl',
                                         'qsbl', 'hbbl', 'gzhb', 'zqhb', 'ysqs', 'yqbl', 'bzbl', 'glbl', 'lxbl',
                                         'sgbl', 'dtbl', 'qtys', 'qttz', 'tzbl', 'dfye', 'fsye', 'fsbl', 'mchg',
                                         'qtfz', 'chbh', 'ggrq', 'recstat', 'checkflag', 'creator', 'modifier',
                                         'checker', 'credt', 'moddt', 'stimestamp', 'gpbd', 'gpjz', 'gjbd', 'hbbd',
                                         'jjtzszhj', 'data_source', 'zxqysmzqsz', 'yqtzsz', 'qqtzsz', 'hbscgjszhj',
                                         'zcxjrz', 'qydqrzq', 'zqpj', 'sycxqcg397tzq', 'bz', 'jrysptzbl', 'qhbl',
                                         'ctpzbl', 'zcxjrzbl', 'qydqrzqbl', 'zqpjbl', 'sycxqcg397tzqbl', 'mdshgdfszcbl',
                                         'qt', 'mdshgdfszc', 'yxg', 'fdc', 'gjs', 'zqjz', 'tycd', 'dfzfz', 'qytz', 'gdsytz', 'cqgqtz',)
                          )
    '''公募持仓资产比例数据'''

    # 指数成分股数据
    MARKET_CFG = UrlCfg('http://%s/data/fund/brinson/lc_icw', 'post','ams',
                        lambda x: {
                            'secuCode': x['secuCode'],
                            'endDate': x['endDate'],
                            'fields': x['fields'],
                            'page': x['page'],
                            'perPage': x['perPage']
                        },
                        lambda y: {},
                        supportFields=('indexcode', 'innercode', 'infosource',
                                       'enddate', 'weight', 'updatetime', 'jsid', 'secucode',)
                        )
    '''指数成分股数据'''

    # 公私募净值归因 - Barra风格因子数据
    BARRA_FACTORY = UrlCfg('http://%s/data/fund/jzgy/barra_factor_return' ,'post','ams',
                                lambda x: {
                                    'tradeDate': {
                                        'startDate': x['startDate'],
                                        'endDate': x['endDate']
                                    },
                                    'fields': x['fields'],
                                    'page': x['page'],
                                    'perPage': x['perPage']
                                },
                                lambda y: {},
                                supportFields=(
                                    'tradeDate', 'factorName', 'factorRet',)
                                )
    '''公私募净值归因 - Barra风格因子数据'''

    #  全量指数行情数据
    MARKET_HQQL = UrlCfg('http://%s/data/fund/jzgy/hqql' ,'post','ams',
                         lambda x: {
                             'zqdm': x['zqdm'],
                             'jyrq': {
                                 'startDate': x['startDate'],
                                 'endDate': x['endDate']
                             },
                             'fields': x['fields'],
                             'page': x['page'],
                             'perPage': x['perPage']
                         },
                         lambda y: {},
                         supportFields=('zqdm', 'scdm', 'jyrq', 'zqmc', 'qspj', 'kpjg', 'spjg',
                                        'zgjg', 'zdjg', 'cjsl', 'cjjs', 'cjbs', 'zdsl', 'zdfd',
                                        'bdfd', 'ltsz', 'zsz', 'pb', 'pe', 'roe', 'gxl',)
                         )
    ''' 全量指数行情数据'''

    #  公私募净值归因 - 板块指数数据
    SECTOR_FACTOR = UrlCfg('http://%s/data/fund/jzgy/sector_factor' ,'post','ams',
                           lambda x: {
                               'tradeDate': {
                                   'startDate': x['startDate'],
                                   'endDate': x['endDate']
                               },
                               'fields': x['fields'],
                               'page': x['page'],
                               'perPage': x['perPage']
                           },
                           lambda y: {},
                           supportFields=(
                               'tradeDate', 'bigfinance', 'consuming', 'tmt', 'cycle', 'manufacture',)
                           )
    ''' 公私募净值归因 - 板块指数数据 '''

    #  私募基金回报数据
    SIMU_RHB = UrlCfg('http://%s/data/fund/jzgy/rhb' ,'post','ams',
                      lambda x: {
                          'jjdm': x['jjdm'],
                          'jzrq': {
                              'startDate': x['startDate'],
                              'endDate': x['endDate']
                          },
                          'fields': x['fields'],
                          'page': x['page'],
                          'perPage': x['perPage']
                      },
                      lambda y: {},
                      supportFields=('jjdm', 'jzrq', 'hbdr',
                                     'hbcl', 'hbfh', 'fqdwjz',)
                      )
    ''' 私募基金回报数据 '''

################################ A股市场/科创板 ################################    
    # A股市场估值数据
    SC_VALUATION_A = UrlCfg('http://%s/data/fund/sac/dfv_stibdifv_a' ,'post','ams',
                          lambda x: {
                              'tradingDay': {
                                  'startDate': x['startDate'],
                                  'endDate': x['endDate']
                              },
                              'fields': x['fields'],
                              'page': x['page'],
                              'perPage': x['perPage']
                          },
                          lambda y: {},
                          supportFields=('innercode', 'tradingday', 'pe', 'pb', 'pcf', 'ps', 'dividendratio', 'updatetime', 'jsid',
                                         'psttm', 'totalmv', 'negotiablemv', 'pelyr', 'pcfttm', 'pcfs', 'pcfsttm', 'dividendratiolyr',
                                         'enterprisevaluew', 'enterprisevaluen', 'inserttime', 'totalmv2', 'totalasmv', 'pettmcut',
                                         'forwardpeqa', 'forwardpehr', 'peg', 'pettmtoorrate', 'forwardpcfqa', 'forwardpcfhr',
                                         'forwardpcfsqa', 'forwardpcfshr', 'forwardpsqa', 'forwardpshr', 'dividendratiolyr2',
                                         'dividendratio2', 'evtoebitda', 'evtoor', 'evtofcff', 'evtocfo', 'evtogp', 'per',
                                         'evtoebitdarandd', 'totalmvtorandd', 'mva', 'floatmva', 'marketvaluetodebt1',
                                         'marketvaluetodebt2', 'debttoassetvalue1', 'debttoassetvalue2',)
                          )
    ''' A股市场估值数据 '''
    # 科创板估值数据
    SC_VALUATION_KC = UrlCfg('http://%s/data/fund/sac/dfv_stibdifv_kc' ,'post','ams',
                          lambda x: {
                              'tradingDay': {
                                  'startDate': x['startDate'],
                                  'endDate': x['endDate']
                              },
                              'fields': x['fields'],
                              'page': x['page'],
                              'perPage': x['perPage']
                          },
                          lambda y: {},
                          supportFields=('innercode', 'tradingday', 'pe', 'pb', 'pcf', 'ps', 'dividendratio', 'updatetime', 'jsid',
                                         'psttm', 'totalmv', 'negotiablemv', 'pelyr', 'pcfttm', 'pcfs', 'pcfsttm', 'dividendratiolyr',
                                         'enterprisevaluew', 'enterprisevaluen', 'inserttime', 'totalmv2', 'totalasmv', 'pettmcut',
                                         'forwardpeqa', 'forwardpehr', 'peg', 'pettmtoorrate', 'forwardpcfqa', 'forwardpcfhr',
                                         'forwardpcfsqa', 'forwardpcfshr', 'forwardpsqa', 'forwardpshr', 'dividendratiolyr2',
                                         'dividendratio2', 'evtoebitda', 'evtoor', 'evtofcff', 'evtocfo', 'evtogp', 'per',
                                         'evtoebitdarandd', 'totalmvtorandd', 'mva', 'floatmva', 'marketvaluetodebt1',
                                         'marketvaluetodebt2', 'debttoassetvalue1', 'debttoassetvalue2',)
                          )
    ''' 科创板估值数据 '''
    # A股市场复权行情数据
    SC_FQ_A = UrlCfg('http://%s/data/fund/brinson/pd_stibpd_a' ,'post','ams',
                          lambda x: {
                              'tradingDay': {
                                  'startDate': x['startDate'],
                                  'endDate': x['endDate']
                              },
                              'fields': x['fields'],
                              'page': x['page'],
                              'perPage': x['perPage']
                          },
                          lambda y: {},
                          supportFields=('id','innercode','tradingday','closeprice','changepct','backwardprice',
                                'risingupdays','fallingdowndays','maxrisingupdays','maxfallingdowndays',
                                'fallondebut','fallonnaps','ahpremiumrate50','stockboard','limitboard',
                                'surgedlimit','declinelimit','highestprice','lowestprice','highestpricerw',
                                'lowestpricerw','highestpricetw','lowestpricetw','highestpricerm','lowestpricerm',
                                'highestpricetm','lowestpricetm','highestpricer3m','lowestpricer3m','highestpricer6m',
                                'lowestpricer6m','highestpriceytd','lowestpriceytd','highestpricer12m','lowestpricer12m',
                                'updatetime','jsid','highestpricermthree','lowestpricermthree','highestpricermsix',
                                'lowestpricermsix','highestpricery','lowestpricery','inserttime',)
                          )
    '''A股市场复权行情数据'''
    #科创板复权行情数据
    SC_FQ_KC = UrlCfg('http://%s/data/fund/brinson/pd_stibpd_kc','post','ams',
                          lambda x: {
                              'tradingDay': {
                                  'startDate': x['startDate'],
                                  'endDate': x['endDate']
                              },
                              'fields': x['fields'],
                              'page': x['page'],
                              'perPage': x['perPage']
                          },
                          lambda y: {},
                          supportFields=('id','innercode','tradingday','closeprice','changepct','backwardprice',
                                'risingupdays','fallingdowndays','maxrisingupdays','maxfallingdowndays',
                                'fallondebut','fallonnaps','ahpremiumrate50','stockboard','limitboard',
                                'surgedlimit','declinelimit','highestprice','lowestprice','highestpricerw',
                                'lowestpricerw','highestpricetw','lowestpricetw','highestpricerm','lowestpricerm',
                                'highestpricetm','lowestpricetm','highestpricer3m','lowestpricer3m','highestpricer6m',
                                'lowestpricer6m','highestpriceytd','lowestpriceytd','highestpricer12m','lowestpricer12m',
                                'updatetime','jsid','highestpricermthree','lowestpricermthree','highestpricermsix',
                                'lowestpricermsix','highestpricery','lowestpricery','inserttime',)
                          )
    '''科创板复权行情数据'''


