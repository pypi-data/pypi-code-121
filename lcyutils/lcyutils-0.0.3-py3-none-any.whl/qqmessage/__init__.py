# %%
import requests


# 支持传入数据直接进行测试并返回结果
def lcy_qqmessage(qq,message):
    if len(qq) < 4:
        return "Wrong QQ number"
    if len(message) == 0:
        return "Empty message"
    headers = {'Content-Type': "application/json",
                'User-Agent':"Mozilla/5.0 (iPhone; CPU iPhone OS 15_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.18(0x18001234) NetType/WIFI Language/zh_CN"}
    messageURL ="http://106.12.127.2:9190/send_private_msg?"
    messageURL = messageURL + "user_id=" + qq + "&"
    messageURL = messageURL + "message=" + message
    data = {
        "user_id":qq,
        "message":message,
    }
    res = requests.post(url=messageURL,data=data,headers=headers)
    return res

def lcy_qqmessage_help():
    print("lcy_qqmessage:\n" \
          "- qq: 你接收消息推送的QQ号\n" \
          "- message: 想要推送的消息，字符串格式\n" \
          "version: beta 0.1\n" \
          "备注：请先加QQ 1794957373\n" \
          "TODO: 更新稳定版\n"
    )

def lcy_qqimage(qq,picurl="https://luochengyu.oss-cn-beijing.aliyuncs.com/img/image-20220525155706948.png"):
    msg = "[CQ:image,file="
    msg = msg + picurl
    msg = msg + "]"
    if picurl == "https://luochengyu.oss-cn-beijing.aliyuncs.com/img/image-20220525155706948.png":
        msg = msg+"默认图片"
    return lcy_qqmessage(qq,msg)


