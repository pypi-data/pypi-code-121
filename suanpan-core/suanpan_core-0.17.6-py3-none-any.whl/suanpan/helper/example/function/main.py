# ----------------------------- 以下是示例程序 -----------------------------
import suanpan
from suanpan.log import logger
from suanpan.simple_run import simple_run


def initialize(init_context):
    """初始化，组件启动时执行一次"""
    logger.info(f"initialize, {init_context}")


def run(context):
    """消息处理，每条消息都会执行"""
    message = context.args
    logger.info(f"message: {message}")
    logger.info('run ...')
    return f'Hello 算盘, {message.inputData1}!'


if __name__ == "__main__":
    simple_run()
