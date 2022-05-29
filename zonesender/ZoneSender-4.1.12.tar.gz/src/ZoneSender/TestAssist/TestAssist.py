import threading

class TestAssist(object):
    def __init__(self) -> None:
        self.TA_TEXT_EVENT_DICT = dict()

    def TA_WaitForTextEvent(self, text: 'str', time_out_ms: 'int') -> 'int':
        ''' 等待字符串, 如果在规定时间等不到就 pass

        :param text: str 要等待的字符串
        :param time_out_ms: int 等待的时间
        :return: int\n
            - 0 在规定时间等到了期望的字符串\n
            - 1 超时, 在规定的时间没有等到期望的字符串\n
            - 2 线程拿不到 Event 对象\n
        '''
        if (text not in self.TA_TEXT_EVENT_DICT.keys()):
            self.TA_TEXT_EVENT_DICT[text] = threading.Event()
        event_ = self.TA_TEXT_EVENT_DICT[text]
        if (not isinstance(event_, threading.Event)):
            return 2
        event_.clear()
        if (not event_.wait(time_out_ms/1000)):
            return 1
        return 0

    def TA_TrigerTextEvent(self, text: 'str') -> None:
        ''' 触发字符串事件

        :param text: str 要触发的字符串，触发后会让所有的等待字符串事件通过
        '''
        if (text not in self.TA_TEXT_EVENT_DICT.keys()):
            return
        event_ = self.TA_TEXT_EVENT_DICT[text]
        if (not isinstance(event_, threading.Event)):
            return
        event_.set()