from typing import Optional
from .hpysignal import main_win_signal  # 给函数用的，不是拿来调用的

io_instance: Optional[open] = None  # 我想用类属性的，但是时间给我干到原来的三倍，傻眼了
output_data: Optional[str] = None  # 测试用的，获取输出框的数据

STRING = 1 << 0
NUM = 1 << 1
FLOAT = 1 << 2
LIST = 1 << 3

ON = 1 << 1
OFF = 1 << 0  # 因为没读到就用这个作为缺省，所以每个参数的(1<<0)就是缺省

# 'output_mode'
RETURN_ONCE = 1 << 0
RETURN_LIST = 1 << 1
RETURN_LIST_OUTPUT_IN_ONE_LINE = 1 << 2
NO_RETURN = 1 << 3
NO_RETURN_SINGLE_FUNCTION = 1 << 4


def write(anything, end="\n") -> None:
    """
    用于向指定的文件流写入，每次写入之后立即刷新缓存区（立即写入硬盘）

    :param anything: 要写入的东西
    :param end: 每次写入在末尾追加的东西，默认为换行符
    :return: None
    """
    io_instance.write(str(anything) + end)
    io_instance.flush()
    return None


def write_without_flush(anything, end="\n") -> None:
    """
    用于向指定的文件流写入，每次写入之后不刷新缓存区，需要手动刷新（使用flush函数）

    :param anything: 要写入的东西
    :param end: 每次写入在末尾追加的东西，默认为换行符
    :return: None
    """
    io_instance.write(str(anything) + end)
    return None


def flush() -> None:
    """
    用于刷新缓存区（将缓存区中的数据写入硬盘）

    :return: None
    """
    io_instance.flush()
    return None


def output(anything) -> None:
    """
    输出到框体

    :param anything: 要输出到框体的数据
    :return: None
    """
    main_win_signal.appendOutPutBox.emit(str(anything))
    return None


def clearOutput() -> None:
    """
    清空输出框

    :return: None
    """
    main_win_signal.clearOutPutBox.emit()
    return None


def setOutput(msg: str) -> None:
    """
    设置输出框的显示数据

    :param msg: 要输出到框体的数据
    :return: None
    """
    main_win_signal.setOutPutBox.emit(msg)
    return None


# 以下是用来传递数据的


def setIoInstance(instance) -> None:
    """
    设置类属性：io实例

    :param instance: io实例
    :return: None
    """
    global io_instance
    io_instance = instance
    return None


def getIoInstance():
    """
    返回io实例

    :return: 类属性：io实例
    """
    return io_instance


def setOutPutData(data: str) -> None:
    """
    设置output_data这个变量

    :return: None
    """
    global output_data
    output_data = data
    return None


def getOutputData():
    """
    获取output_data这个变量

    :return: OutputData
    """
    main_win_signal.getOutPutBox.emit()
    return output_data


def addOne(num: int) -> int:
    """
    用于测试的函数，会输出输入数字+1的结果

    :param num: 一个数字
    :return: int
    """
    return num + 1
