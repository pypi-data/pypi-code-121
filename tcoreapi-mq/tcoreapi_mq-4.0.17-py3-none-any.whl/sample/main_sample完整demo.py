import time
from tcoreapi_mq import *
import pandas as pd
#登入
TCoreAPI= TCoreZMQ(quote_port="51630",trade_port="51600")
#TCoreAPI= TCoreZMQ(quote_port="51864",trade_port="51834")
#TCoreAPI= TCoreZMQ(quote_port="51424",trade_port="51394")
#查询指定合约信息
print("查询指定合约：",TCoreAPI.QueryInstrumentInfo("TC.O.SSE.510050.202108.C.3.6"))
#查询HOT对应的指定月合约
    #参数：
    #####symbol：TC.F.SHFE.rb.HOT
    #####Time:
    #        "20220105013000" yyyymmddHHMMSS带入该参数返回参数指定时间HOT对应的指定月{'20211116070001': 'TC.F.SHFE.rb.202205'}，其中Key为换月时间，Value为对应的指定月合约    
    #        ""不带入该参数时，返回HOT所有历史的换月记录
hotsymb=TCoreAPI.GetHotChange("TC.F.SHFE.rb.HOT","20220105013000")
print(hotsymb)

'''
.
.
-2:实值两档期权合约
-1:实值一档期权合约
0:平值期权合约
1:虚值期权合约
.
.
'''
ATMsym=GetATM("TC.O.SSE.510050.202201", 1)#获取510050期权202201月份的虚值1档期权合约代码
print(ATM)

#查询指定类型合约列表
#参数1：
    #期货：Future
    #期权：Options
    #证券：Stock
#参数2：指定日期的合约列表，如果不带或带入空参数，返回最新的合约列表，否则返回指定日期的合约列表
symbollist=TCoreAPI.QueryAllInstrumentInfo("Options","20210824")
#print("查询合约：\n",symbollist)
#解析期权合约列表
if symbollist['Success']=="OK":
    for opt in symbollist['Instruments']['Node']:
        #SSE交易所的期权
        if opt['ENG']=='SSE(O)':
            for optlist in opt['Node']:
                #标的50etf的琪琪
                if optlist['ENG_M']=='50ETF':
                    for optlist2 in optlist['Node']:
                        #202108月份合约
                        if optlist2['ENG']=='202108':
                            for syblist in optlist2['Node']:
                                for symb in syblist['Contracts']:
                                    print(symb)
#解除订阅
#TCoreAPI.UnsubQuote("TC.F.CFFEX.IF.202106")
#订阅实时行情
TCoreAPI.SubQuote("TC.O.SSE.510050.202108.C.3.2")
#解除订阅
#TCoreAPI.UnsubGreeks("TC.F.U_SSE.510050.202106")
#订阅实时Greeks行情
#TCoreAPI.SubGreeks("TC.F.U_SSE.510050.202106")

#获取历史数据
    #1：合约代码，
    #2：数据周期:
        ##标准行情历史数据
        # tick: "TICKS", 
        # 分K: "1K",
        # 日K: "DK"，
        ##DOGS为包含Greeks、标的期货、标的合约的历史数据
        # DOGS秒："DOGSS", 
        # DOGS分K："DOGSK"
    #3: 历史数据开始时间,
    #4: 历史数据结束时间
#his=TCoreAPI.SubHistory("TC.F.U_SSE.510050.202106", "DOGSK", "2021050100", "2021052107")
his=TCoreAPI.SubHistory("TC.O.SSE.510050.202108.C.3.6", "1K", "2021062300", "2021062307")
print("历史数据：\n",his)

#查询已登入资金账户
accountInfo = TCoreAPI.QryAccount()
#查询当日委托回报
reportData = TCoreAPI.QryReport()
if reportData:
    print("当日委托回报：\n",pd.DataFrame(reportData))
else:
    print("今日没有委托记录")
#查询当日成交回报
fillReportData = TCoreAPI.QryFillReport()
if fillReportData:
    print("当日成交回报：\n",pd.DataFrame(fillReportData))
else:
    print("今日没有成交记录")
#查询持仓监控
PositionTracker=TCoreAPI.QryPositionTracker()
if PositionTracker:
    print("持仓监控信息：\n",PositionTracker)
else:
    print("没有持仓监控信息")
strAccountMask =""
if accountInfo != None:
    arrInfo = accountInfo["Accounts"]
    if len(arrInfo) != 0:
        for acc in arrInfo:
            print("当前已登入资金账户\n",pd.DataFrame.from_dict(acc,orient='index').T)
        #获取账户列表中的第一个账户
        strAccountMask = arrInfo[0]["AccountMask"]
        #查询资金
        margin=TCoreAPI.QryMargin(strAccountMask)
        print("资金信息：\n",pd.DataFrame(margin["Margins"]))
        #查询持仓
        pos = TCoreAPI.QryPosition(strAccountMask)
        print("持仓信息：\n",pd.DataFrame(pos))
        #建组合
        orders_obj = {
                    "Symbol":"TC.O.SSE.510050.202106.C.3.6&TC.O.SSE.510050.202106.C.3.7",
                    "BrokerID":arrInfo[0]['BrokerID'],
                    "Account":arrInfo[0]['Account'],
                    "CombDirection":"1",
                    "Side":"1",
                    "CombinationType":"1",
                    "Volume":"1"
                    }
        TCoreAPI.OptComb(orders_obj)
        #查询新建组合的委托回报
        TCoreAPI.QryOptCombOrder(strAccountMask)
        #查询组合持仓
        OptCombPos=TCoreAPI.QryOptCombPosition(strAccountMask)
        if len(OptCombPos)!=0:
            #拆分组合，将查询到的第一个组合持仓拆分
            orders_obj = {
                "Symbol":OptCombPos[0]['Symbol'],
                "BrokerID":arrInfo[0]['BrokerID'],
                "Account":arrInfo[0]['Account'],
                "CombDirection":"2",
                "Side":OptCombPos[0]['Side'],
                "CombinationType":OptCombPos[0]['CombinationType'],
                "Volume":"1",
                "OptCombID":OptCombPos[0]['OptCombID']
            }
            TCoreAPI.OptComb(orders_obj)

flag=True
while True:
    #行情更新
    quoteupdate= TCoreAPI.mdupdate()

    if quoteupdate:
        if quoteupdate['DataType']=='REALTIME':
            print("实时行情: \n",pd.DataFrame.from_dict(quoteupdate['Quote'],orient='index').T)  #这里只是展示用，实际应用建议不要使用dataframe转换实时数据，会影响运行效率
            if strAccountMask !="" and flag:
                #新增一笔委托
                orders_obj = {
                                "Symbol":quoteupdate['Quote']['Symbol'],
                                "BrokerID":arrInfo[0]['BrokerID'],
                                "Account":arrInfo[0]['Account'],
                                "Price":"0.0001",#quoteupdate['Quote']['LowPrice'],
                                "TimeInForce":"1",
                                "Side":"1",
                                "OrderType":"2",
                                "OrderQty":"1",
                                "PositionEffect":"4",
                                "SelfTradePrevention":"3"
                                #"ChasePrice":"1T|5|3|M"
                            }
                ordid = TCoreAPI.NewOrder(orders_obj)
                if ordid!=None:
                    while True:
                        if TCoreAPI.getorderinfo(ordid):
                            print("新增委托",TCoreAPI.getorderinfo(ordid)['ReportID'])#,TCoreAPI.QryReport()[-1]['ReportID'])
                            break

                #改单
                time.sleep(1)
                print(TCoreAPI.getorderinfo(ordid)['ExecType'])
                reporders_obj={
                    "ReportID":TCoreAPI.getorderinfo(ordid)['ReportID'],#TCoreAPI.QryReport()[-1]['ReportID'],
                    "ReplaceExecType":"0",
                    "Price":quoteupdate['Quote']['TradingPrice']
                    }
                #在可改单的委托单状态下发送改单指令（注意：模拟交易和外盘允许改单，内盘建议使用先删单单然后发送新委托方式改单）
                if TCoreAPI.getorderinfo(ordid)['ExecType'] in ["0","1","4","6"]:
                    reorder=TCoreAPI.ReplaceOrder(reporders_obj)
                    print("修改委托单：\n",reorder,TCoreAPI.QryReport()[-1]['ReportID'])
                #取消委托单
                time.sleep(1)
                cancalorders_obj = {
                            "ReportID":TCoreAPI.getorderinfo(ordid)['ReportID'],#TCoreAPI.QryReport()[-1]['ReportID'],
                            }
                #在可删单的委托单状态下发送删单指令      
                if TCoreAPI.getorderinfo(ordid)['ExecType'] in ["0","1","4","6"]:
                    cancal_order = TCoreAPI.CancelOrder(cancalorders_obj )
                    print("删单:",cancal_order)
                flag=False

        elif  quoteupdate['DataType']=="GREEKS":
            print("实时GREEKS: \n",pd.DataFrame.from_dict(quoteupdate['Quote'],orient='index').T)      
    #交易更新
    tradeupdate= TCoreAPI.tdupdate()
    if tradeupdate:
        if tradeupdate['DataType']=='ACCOUNTS':
            print("账户列表更新: \n",tradeupdate['Accounts'])
            arrInfo = tradeupdate['Accounts']
            if len(arrInfo) != 0:
                strAccountMask = arrInfo[0]["AccountMask"]
        elif tradeupdate['DataType'] == "EXECUTIONREPORT":
            print("实时委托回报: \n",pd.DataFrame.from_dict(tradeupdate["Report"],orient='index').T)
        elif tradeupdate['DataType'] == "FILLEDREPORT":
            print("实时成交: \n",pd.DataFrame.from_dict(tradeupdate["Report"],orient='index').T)
        elif tradeupdate['DataType'] == "POSITIONTRACKER":
            #查询持仓监控
            PositionTracker=TCoreAPI.QryPositionTracker()
            #print("持仓监控信息更新\n",PositionTracker)