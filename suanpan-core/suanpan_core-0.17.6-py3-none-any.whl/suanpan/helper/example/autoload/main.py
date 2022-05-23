import suanpan
from suanpan.app import app
from runtime import autoLoadSave


@app
@autoLoadSave
def main(args):
    """
    获取输入端口数据方式:
        输入端口1： args.inputData1;
        输入端口2： args.inputData2...
        注：请在节点输入桩具体类型中配置数据类型，或自行转换
    发送至输出端口数据方式:
        单输出： return result
        多输出端口： {"out1": result1, "out2": result2...}
        发送某个端口：{"out2": result}
        注：请在节点输出桩具体类型中配置数据类型，否则下游节点可能会报错！
    获取参数列表参数值方式: args.param1, args.param2...args.param20
        注：默认载入的参数值为string, 如需转换请自行适配, 例如: int(args.param1)
    """
    # 在此处编辑用户自定义代码
    result = args.inputData1
    return f"Hello suanpan, I got in1: {result}"


if __name__ == "__main__":
    suanpan.run(app)
