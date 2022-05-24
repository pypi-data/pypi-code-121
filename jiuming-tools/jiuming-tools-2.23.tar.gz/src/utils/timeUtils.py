import time


def count_time(info="计时"):
    """
    装饰函数   为函数装饰计算耗时
    :param info: 名称
    :return:
    """

    def _count_time(func):
        def _wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            print("{}耗时:{}μs,结果:{}".format(info, str(
                round((int(round((end_time - start_time) * 1000000))), 2)), str(result)))
            return result

        return _wrapper

    return _count_time
