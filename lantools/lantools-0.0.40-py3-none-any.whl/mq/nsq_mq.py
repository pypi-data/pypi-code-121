import nsq
import requests
from .mq import Writer, Reader

# NSQ 的api支持的不好，暂时使用http接口，性能不好
class NsqWriter(Writer):
    def __init__(self, *, addrs, topic):
        
        self.url = "http://{}/pub?topic={}".format(
            addrs[0], 
            topic
        )

    def write(self, message, *, callback=None):
        requests.post(self.url , data=message)

class NsqReader(Reader):
    def run(self, callback):
        def _mission(message):
            if message.body:
                is_finish = callback(message.body, message=message)
                if is_finish==True:
                    message.finish()
            else:
                message.finish()

            return True

        nsq.Reader(
            message_handler=_mission,
            **self.options
        )

        nsq.run()      