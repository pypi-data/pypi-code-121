import os

from common.config.config import CONFIG_PATH

from common.common.constant import Constant
from common.plugin.data_bus import DataBus
from common.plugin.file_plugin import FilePlugin
from common.common.api_driver import APIDriver


class ServicePlatForm(object):

    @classmethod
    def sendMsg(self,content, _list):
        for _index in range(len(_list)):
            _arr = str(_list[_index]).split('&')
            os.environ['toUserId'] = str(_arr[0]).lower()
            os.environ['toMail'] = str(_arr[1])
            DataBus.set_key('content',content)
            _data=FilePlugin.load_file("muc.xml",file_path=CONFIG_PATH).encode()
            APIDriver.http_request(url=DataBus.get_key(Constant.MSG_URL),method='post',parametric_key='data',data=_data)

if __name__ == '__main__':
    print(ServicePlatForm.sendMsg("aa","bb"))

