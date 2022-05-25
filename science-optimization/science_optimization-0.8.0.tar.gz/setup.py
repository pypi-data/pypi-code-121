from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
import setuptools
import subprocess


class GetPybindInclude(object):
    """Helper class to determine the pybind11 include path

    The purpose of this class is to postpone importing pybind11
    until it is actually installed, so that the ``get_include()``
    method can be invoked."""

    def __init__(self, user=False):
        try:
            import pybind11
        except ImportError:
            if subprocess.call([sys.executable, "-m", "pip", "install", "pybind11"]):
                raise RuntimeError("pybind11 install failed.")

        self.user = user

    def __str__(self):
        import pybind11

        return pybind11.get_include(self.user)


ext_modules = [
    Extension(
        "nlpalg",
        [
            "src/nlpalg.cpp",
        ],
        include_dirs=[
            # Path to pybind11 headers
            GetPybindInclude(),
            GetPybindInclude(user=True),
        ],
        language="c++",
    ),
]


# As of Python 3.6, CCompiler has a `has_flag` method.
# cf http://bugs.python.org/issue26689
def has_flag(compiler, frag_name):
    """Return a boolean indicating whether a flag name is supported on
    the specified compiler.
    """
    import tempfile

    with tempfile.NamedTemporaryFile("w", suffix=".cpp") as f:
        f.write("int main (int argc, char **argv) { return 0; }")
        try:
            compiler.compile([f.name], extra_postargs=[frag_name])
        except setuptools.distutils.errors.CompileError:
            return False
    return True


def cpp_flag(compiler):
    """Return the -std=c++[11/14] compiler flag.
    The c++14 is prefered over c++11 (when it is available).
    """
    if has_flag(compiler, "-std=c++14"):
        return "-std=c++14"
    elif has_flag(compiler, "-std=c++11"):
        return "-std=c++11"
    else:
        raise RuntimeError(
            "Unsupported compiler -- at least C++11 support " "is needed!"
        )


class BuildExt(build_ext):
    """A custom build extension for adding compiler-specific options."""

    c_opts = {
        "msvc": ["/EHsc"],
        "unix": [],
    }

    if sys.platform == "darwin":
        c_opts["unix"] += ["-stdlib=libc++", "-mmacosx-version-min=10.7"]

    def build_extensions(self):
        ct = self.compiler.compiler_type
        opts = self.c_opts.get(ct, [])
        if ct == "unix":
            opts.append('-DVERSION_INFO="%s"' % self.distribution.get_version())
            opts.append(cpp_flag(self.compiler))
            if has_flag(self.compiler, "-fvisibility=hidden"):
                opts.append("-fvisibility=hidden")
        elif ct == "msvc":
            opts.append('/DVERSION_INFO=\\"%s\\"' % self.distribution.get_version())
        for ext in self.extensions:
            ext.extra_compile_args = opts
        build_ext.build_extensions(self)


# read description
with open("README.md", "r") as fh:
    long_description = fh.read()

# read requirements
install_requires = [
    "cycler~=0.11",
    "decorator~=5.1",
    "joblib~=1.1",
    "kiwisolver~=1.3",
    "matplotlib~=3.4",
    "networkx~=2.6",
    "numpy~=1.21",
    "ortools~=9.1",
    "pandas~=1.3",
    "Pillow~=8.4",
    "protobuf~=3.19",
    "pybind11~=2.8",
    "pyparsing~=3.0",
    "python-dateutil~=2.8",
    "pytz~=2021.3",
    "PyWavelets~=1.1",
    "scipy~=1.7",
    "six~=1.16",
    "xlrd~=2.0",
    "pybind11>=2.2",
]

setup(
    name="science_optimization",
    version="0.8.0",
    author="ENACOM",
    author_email="matheus.mendonca@enacom.com.br",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=install_requires,
    packages=setuptools.find_packages(),
    ext_modules=ext_modules,
    cmdclass={"build_ext": BuildExt},
    description="A framework for optimization.",
)
