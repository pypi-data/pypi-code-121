from setuptools import setup
from torch.utils.cpp_extension import BuildExtension, CUDAExtension

setup(
    name="emdcuda",
    ext_modules=[
        CUDAExtension(  # type: ignore
            "emdcuda",
            [
                "/".join(__file__.split("/")[:-1] + ["emd_cuda_cu.cu"]),
                "/".join(__file__.split("/")[:-1] + ["emd_cuda_cpp.cpp"]),
            ],
        ),
    ],
    cmdclass={"build_ext": BuildExtension},
)
