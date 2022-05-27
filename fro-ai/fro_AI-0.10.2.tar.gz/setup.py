import setuptools
import codecs
import os.path


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


setuptools.setup(
    name="fro_AI",  # Replace with your own username
    version=get_version("fro_AI/__init__.py"),
    author="z14git",
    author_email="lzl1992@gmail.com",
    description="A package for easy use of AI application",
    url="https://gitee.com/z14git/fro_-ai",
    extras_require={
        'all': ['torch', 'torchvision', 'opencv-python', 'flask'],
    },
    install_requires=['tqdm', 'six', 'loguru'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    package_data={
        'fro_AI.face_evoLve': ['align/*.npy'],
        'fro_AI': ['data/*.txt'],
        'fro_AI.utils': ['templates/index.html']
    },
)
