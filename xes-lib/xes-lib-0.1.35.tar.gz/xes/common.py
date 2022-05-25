import sys
import json
import time

def getCookies():
    cookies = ""
    if len(sys.argv) > 1:
        try:
            cookies = json.loads(sys.argv[1])["cookies"]
        except:
            pass
    return cookies

def jsonLoads(str):
    try:
        return json.loads(str)
    except:
        return None

# Information Transfer Protocol
# Information exchange Protocol
# 信息交换输出工具函数
def InfoTransferAndExchange(data):
	time.sleep(0.01)
	jsonStr = json.dumps(data)
	print("#xzeysx#" + jsonStr + "#xzeysx#")

'''
	// 提示信息
    data = { 'type':'msg','value': "识别前图片："+img_src }
    XesUtils.InfoTransferAndExchange(data)

	// 结果信息
	data = { 'type':'result','desc':'识别后图片','value' : imgurl }
    XesUtils.InfoTransferAndExchange(data)
'''