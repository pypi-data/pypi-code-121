from .TestAssist import TestAssist
from .ZoneSenderStone import ZoneSenderStone


class ZoneSenderApp(ZoneSenderStone):
    '''
    ZoneSender 的职能类，可以用来实现对硬件以及各种协议栈的完全控制\n
    该类继承于 ZoneSender.ZoneSenderFramework\n
    该类有几个事件触发型的函数，用户如果需要逻辑仿真的功能。\n
    必须重写下面的几个函数来实现自己的功能:\n
        - OnCanFrame\n
        - OnCanPdu\n
        - OnCanSignal\n
        - OnCanMessage\n
        - OnSomeipPackage\n
    该对象有几个成员变量，可以查看相应的对象介绍页面来了解函数列表:\n
        - CanStack: ZoneSender.CanStackNodeClient\n
        - CanParser: ZoneSender.CanParserNodeClient\n
        - SomeipStack: ZoneSender.SomeipNodeClient\n
    通过调用几个成员变量的函数实现各种控制功能\n
    '''
    def __init__(self) -> None:
        super().__init__()
        self.TA = TestAssist()
