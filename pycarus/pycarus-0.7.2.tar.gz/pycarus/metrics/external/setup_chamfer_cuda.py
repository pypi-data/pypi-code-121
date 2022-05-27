from setuptools import setup
from torch.utils.cpp_extension import BuildExtension, CUDAExtension

setup(
    name="chamfercuda",
    ext_modules=[
        CUDAExtension(  # type: ignore
            "chamfercuda",
            [
                "/".join(__file__.split("/")[:-1] + ["chamfer_cuda_cpp.cpp"]),
                "/".join(__file__.split("/")[:-1] + ["chamfer_cuda_cu.cu"]),
            ],
        ),
    ],
    cmdclass={"build_ext": BuildExtension},
)
