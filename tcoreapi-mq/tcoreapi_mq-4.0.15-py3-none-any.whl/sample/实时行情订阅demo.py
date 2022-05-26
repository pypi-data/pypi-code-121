from tcoreapi_mq import * 
import datetime

#登入
TCoreAPI= TCoreZMQ(quote_port="51630",trade_port="51600")


#订阅合约实时行情报价
#订阅单个合约参数str或list
TCoreAPI.SubQuote("TC.F.SHFE.rb.HOT")
#订阅多个合约list
#TCoreAPI.SubQuote(["TC.F.SHFE.rb.202110","TC.F.CFFEX.IF.202106"])

#订阅合约的Greeks实时数据
#订阅单个合约参数str或list,订阅多个合约list
TCoreAPI.SubGreeks(["TC.F.U_SSE.510050.202201"])

while True:
    message=TCoreAPI.mdupdate()
    if message:
        if message['DataType']=='REALTIME':
            print("实时行情 \n 合约：",datetime.datetime.now(),message['Quote']['Symbol'],"  ",int(message['Quote']['FilledTime'])+80000,"  当日成交量：%s" % message['Quote']['TradeVolume'])
        elif  message['DataType']=="GREEKS":
            print("实时GREEKS \n IV:",datetime.datetime.now(),message['Quote'])
