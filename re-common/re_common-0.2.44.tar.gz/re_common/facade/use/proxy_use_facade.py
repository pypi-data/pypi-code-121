import time


def set_school_list_proxy(self):
    """
    使用该函数条件, self为类的对象
    代理在 proxyset set里
    使用的是bshttpx这个变量
    """
    try:
        proxy = self.proxyset.pop()
        self.logger.info("proxy is:{},proxy size is: {}".format(proxy, len(self.proxyset)))
        return self.bshttpx.creat_sn(proxy=proxy,
                                     headers=self.headers,
                                     verify=False)
    except KeyError as e:
        time.sleep(15)
        if str(e) == "'pop from an empty set'":
            self.proxyset = set(self.school_proxy_list)
            return self.set_school_list_proxy()