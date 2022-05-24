class MsgInfo(object):
    """
    消息体结构，没有想好如何使用
    """

    def __init__(self, code, msg, traceback, info_dict=None):
        self.code = code  # 状态码
        self.msg = msg
        self.traceback = traceback
        if info_dict is None:
            info_dict = {}
        self.info_dict = info_dict
        # 多个消息历史的列表
        self.msg_list = []

    def msg_lists(self):
        """
        将消息结构list存放，而不是嵌套
        :return:
        """
        self.msg_list.append({"code": self.code,
                              "msg": self.msg,
                              "traceback": self.traceback,
                              "info_dict": self.info_dict})
        return self
