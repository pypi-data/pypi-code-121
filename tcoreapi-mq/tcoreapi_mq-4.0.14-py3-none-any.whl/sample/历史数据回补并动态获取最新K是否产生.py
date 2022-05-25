import time
from tcoreapi_mq import * 
import numpy as np
import pandas as pd

#登入
TCoreAPI= TCoreZMQ(quote_port="51630",trade_port="51600")
symbol="TC.F.CFFEX.IF.202205"
TCoreAPI.SubQuote(symbol)
hisdk=TCoreAPI.SubHistory(symbol, "DK", "2022012000", "2022051607")#time.strftime("%Y%m%d",time.localtime()
his5k=TCoreAPI.SubHistory(symbol, "5K", "2022012000", "2022051607")
print("历史数据：\n",pd.DataFrame(hisdk),"\n",pd.DataFrame(his5k))

while True:
    message=TCoreAPI.mdupdate()
    if message and message['DataType']=='REALTIME':
        print("实时行情 \n 合约：",message['Quote'])
        print("实时行情 \n 合约：",datetime.datetime.now(),message['Quote']['Symbol'],"  ",int(message['Quote']['FilledTime'])+80000,"  当日成交量：%s" % message['Quote']['TradeVolume'])
        hisdk=TCoreAPI.barupdate2("DK",hisdk,message)
        his5k=TCoreAPI.barupdate2("5K",his5k,message)
        if len(his5k)>barlen and barlen!=0: #每当5分K的新K产生时计算策略
            ma20=np.mean([float(x["Close"]) for x in hisdk[-21:-2]])
            std20=np.std([float(x["Close"]) for x in his5k[-21:-2]])
            bollup=ma20+2*std20
            bolldown=ma20-2*std20
            pos=(float(his5k[-2]["Close"])-bolldown)/(bollup-bolldown) #新K的Open价格形成时用上一根完整K的close参与计算，当根K只有open，收盘未产生不参与计算
            vanna=0.1*(pos-0.5)
            print(pos,"  ",vanna)
        barlen=len(his5k)
        #print("历史数据：\n",pd.DataFrame(hisdk),"\n",pd.DataFrame(his5k))
