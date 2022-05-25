import argparse
import tensorrt as trt


def main():
    """将onnx文件转换为tensorRT引擎文件

    Args:
        max_workspace_size: int类型,二进制式工作空间大小
        target_engine_path= str类型,输出的引擎文件路径
        onnx_file_path= str类型,输入的onnx文件路径

    Returns:
        无

    """

    # 获取参数
    parser = argparse.ArgumentParser()
    parser.add_argument('--max_workspace_size', '-s', default=28)
    parser.add_argument('--target_engine_path', '-t', default="./test.engine")
    parser.add_argument('--onnx_file_path', '-o', default="./test.onnx")
    parser.add_argument('--min_shape', '-i', default=None)
    parser.add_argument('--opt_shape', '-p', default=None)
    parser.add_argument('--max_shape', '-a', default=None)
    parser.add_argument('--fp16', default=False)
    opt = parser.parse_args()

    # 定义记录器
    logger = trt.Logger(trt.Logger.WARNING)
    builder = trt.Builder(logger)

    # 组件网络
    network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
    parser = trt.OnnxParser(network, logger)

    # 测试是否成功
    parser.parse_from_file(opt.onnx_file_path)
    for idx in range(parser.num_errors):
        print(parser.get_error(idx))
    config = builder.create_builder_config()
    config.max_workspace_size = 1 << opt.max_workspace_size  # 1 MiB

    # 开启fp16模式
    if opt.fp16:
        config.set_flag(trt.BuilderFlag.FP16)

    # 动态尺寸
    if opt.min_shape:
        profile = builder.create_optimization_profile()
        profile.set_shape(network.get_input(0).name, opt.min_shape, opt.opt_shape, opt.max_shape)
        config.add_optimization_profile(profile)

    # tensorRT8的教程格式
    # config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, 1 << 28) # 1 MiB
    serialized_engine = builder.build_serialized_network(network, config)
    with open(opt.target_engine_path, "wb") as f:
        f.write(serialized_engine)