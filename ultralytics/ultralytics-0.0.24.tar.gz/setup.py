import re
from pathlib import Path
from urllib import request

from setuptools import find_packages, setup

# Settings
FILE = Path(__file__).resolve()
ROOT = FILE.parent  # YOLOv5 root directory

# The text of the README file
# README = (ROOT / "README.md").read_text(encoding="utf-8")
README = request.urlopen('https://raw.githubusercontent.com/ultralytics/hub/master/README.md').read().decode('utf-8')


def get_version():
    file = ROOT / 'src/ultralytics/__init__.py'
    return re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', file.read_text(), re.M).group(1)


setup(
    name="ultralytics",  # name of pypi package
    version=get_version(),  # version of pypi package
    python_requires=">=3.7.0",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/ultralytics/yolov5",
    author="Ultralytics",
    author_email='hello@ultralytics.com',
    package_dir={'': 'src'},  # Optional, use if source code is in a subdirectory under the project root, i.e. `src/`
    packages=find_packages('src'),  # Required
    include_package_data=True,
    install_requires=[
        'PyYAML>=5.3.1', 'requests', 'GitPython>=3.1.24', 'torch>=1.7.0', 'torchvision>=0.8.1', 'psutil', 'IPython'],
    extras_require={'tests': [
        'pytest',
        'pytest-cov',
        'coverage', ]},
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows"],
    keywords="machine-learning, deep-learning, ML, AI, PyTorch, object-detection, vision, YOLO, YOLOv3, YOLOv4, YOLOv5")
