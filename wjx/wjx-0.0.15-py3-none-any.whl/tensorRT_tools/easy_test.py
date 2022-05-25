import numpy as np
import os
import pycuda.driver as cuda
import pycuda.autoinit
import tensorrt as trt


def prepare_engine(
    engine_path: str,
    print_info=False,
    input_data_shape=None,
):
    """读取引擎文件

    Args:
        engine_path: str类型,tensorRT引擎文件路径
        print_info: 打印引擎binding信息
        input_data_shape: 输入图片的尺寸

    Returns:
        tensorRT推理所需

    """

    # 创建tensorRT的记录器
    TRT_LOGGER = trt.Logger(trt.Logger.INFO)

    # 获取引擎和语境
    assert os.path.exists(engine_path)
    f = open(engine_path, "rb")
    runtime = trt.Runtime(TRT_LOGGER)
    engine = runtime.deserialize_cuda_engine(f.read())
    context = engine.create_execution_context()

    if input_data_shape:
        context.set_binding_shape(0, input_data_shape)

    # 输出的缓冲区和计算区
    outputs_buffer = []
    outputs_memory = []
    bindings = []

    # 申请空间
    for location, binding in enumerate(engine):

        # 获取每个binding的信息并申请空间
        size = trt.volume(context.get_binding_shape(location))
        dtype = trt.nptype(engine.get_binding_dtype(binding))

        # 打印binding的信息
        if print_info:
            print("Binding name:", engine.get_binding_name(location))
            print("Binding size:", size)
            print("Binding size:", dtype)

        # 申请空间
        buffer = cuda.pagelocked_empty(size, dtype)
        memory = cuda.mem_alloc(buffer.nbytes)

        # Append the device buffer to device bindings.
        bindings.append(int(memory))

        # Append to the appropriate list.
        if engine.binding_is_input(binding):
            input_memory = memory
        else:
            outputs_buffer.append(buffer)
            outputs_memory.append(memory)

    stream = cuda.Stream()
    f.close()

    return (context, bindings, stream, input_memory, outputs_buffer, outputs_memory)


def inference_with_prepare_engine(
    input_data: np.ndarray,
    output_shape: list,
    inference_need,
):
    """读取引擎文件

    Args:
        input_data: ndarra类型,tensorRT引擎文件路径
        inference_need: 从prepare_engine返回
        output_shape: 输出的shape列表
        
    Returns:
        tensorRT的推理结果

    """

    context, bindings, stream, input_memory, outputs_buffer, outputs_memory = inference_need
    input_data = np.ascontiguousarray(input_data)
    cuda.memcpy_htod_async(input_memory, input_data, stream)

    # 推理
    context.execute_async_v2(bindings=bindings, stream_handle=stream.handle)

    # 将输出数据从内存区读出缓存区
    for output_buffer, output_memory in zip(outputs_buffer, outputs_memory):
        cuda.memcpy_dtoh_async(output_buffer, output_memory, stream)

    # Synchronize the stream
    stream.synchronize()

    # reshape输出
    outputs = outputs_buffer[::-1]
    for location, shape in enumerate(output_shape):
        outputs[location] = outputs[location].reshape(shape)

    return outputs


def onnx2trt(
    max_workspace_size=28,
    target_engine_path="./test.engine",
    onnx_file_path="./test.onnx",
    min_shape=None,
    opt_shape=None,
    max_shape=None,
    fp16=False,
):
    """将onnx文件转换为tensorRT引擎文件

    Args:
        max_workspace_size: int类型,二进制式工作空间大小
        target_engine_path= str类型,输出的引擎文件路径
        onnx_file_path= str类型,输入的onnx文件路径

    Returns:
        无

    """

    # 定义记录器
    logger = trt.Logger(trt.Logger.WARNING)
    builder = trt.Builder(logger)

    # 组件网络
    network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
    parser = trt.OnnxParser(network, logger)

    # 测试是否成功
    parser.parse_from_file(onnx_file_path)
    for idx in range(parser.num_errors):
        print(parser.get_error(idx))
    config = builder.create_builder_config()
    config.max_workspace_size = 1 << max_workspace_size  # 1 MiB

    # 开启fp16模式
    if fp16:
        config.set_flag(trt.BuilderFlag.FP16)

    # 动态尺寸
    if min_shape:
        profile = builder.create_optimization_profile()
        profile.set_shape(network.get_input(0).name, min_shape, opt_shape, max_shape)
        config.add_optimization_profile(profile)

    # tensorRT8的教程格式
    # config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, 1 << 28) # 1 MiB
    serialized_engine = builder.build_serialized_network(network, config)
    with open(target_engine_path, "wb") as f:
        f.write(serialized_engine)