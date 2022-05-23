import os
from matplotlib.style import library
import numpy
from Cython.Build import cythonize

def configuration(parent_package='', top_path=None):
    from numpy.distutils.misc_util import Configuration

    config = Configuration('AKM', parent_package, top_path)

    cpp_version = "c++11"

    if os.name == "nt":
        ext_comp_args = ['/']
        ext_link_args = []

        library_dirs = []
        libraries = []
    else:
        ext_comp_args = ['-fopenmp']
        ext_link_args = ['-fopenmp']

        # library_dirs = ["/opt/intel/mkl/lib/intel64", "/usr/lib/openmpi"]
        # libraries = ["m", "mkl_scalapack_lp64", "mkl_cdft_core", "mkl_core", "mkl_intel_lp64", "mkl_blacs_intelmpi_lp64", "mkl_gnu_thread", "gomp", "pthread", "dl", "mpi_cxx", "mkl_def"]
        library_dirs = []
        # libraries = ["m", "blas"]
        libraries = ["m"]

    define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]

    file_path = os.path.dirname(__file__)
    eigen_path = os.path.join(file_path, "Egien400")

    cyname = "AngleKMeans_"
    config.add_extension(cyname,
                         sources=[f'{cyname}.pyx'],
                         include_dirs = [numpy.get_include(), eigen_path],
                         language="c++",

                         extra_compile_args=ext_comp_args,
                         extra_link_args=ext_link_args,

                         library_dirs=library_dirs,
                         libraries=libraries,
                         depends=[f"{cyname}.pxd", f"{cyname}.pyx", "./Eigen400"]
                         #  define_macros=cg.define_macros,
                         )


    config.ext_modules = cythonize(config.ext_modules, compiler_directives={'language_level': 3})

    return config


if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())
