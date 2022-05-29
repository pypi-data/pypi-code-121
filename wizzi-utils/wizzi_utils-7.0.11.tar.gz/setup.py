from distutils.core import setup
# noinspection PyUnresolvedReferences
import setuptools

"""
see https://docs.python.org/3/distutils/setupscript.html
"""

# Read in README.md for our long_description
import os

cwd = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(cwd, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='wizzi_utils',
    packages=[  # main package and sub packages
        'wizzi_utils',  # package name
        'wizzi_utils/misc',  # main sub package
        'wizzi_utils/misc/test',
        # 'wizzi_utils/algorithms',
        # 'wizzi_utils/algorithms/test',
        # 'wizzi_utils/coreset',
        # 'wizzi_utils/coreset/test',
        'wizzi_utils/google',
        'wizzi_utils/google/test',
        'wizzi_utils/json',
        'wizzi_utils/json/test',
        'wizzi_utils/open_cv',
        'wizzi_utils/open_cv/test',
        'wizzi_utils/pyplot',
        'wizzi_utils/pyplot/test',
        'wizzi_utils/socket',
        'wizzi_utils/socket/test',
        'wizzi_utils/torch',
        'wizzi_utils/torch/test',
        # 'wizzi_utils/tensorflow',
        # 'wizzi_utils/tensorflow/test',
        'wizzi_utils/tflite',
        'wizzi_utils/tflite/test',
        'wizzi_utils/tts',
        'wizzi_utils/tts/test',
        'wizzi_utils/models',
        'wizzi_utils/models/cv2_models',
        'wizzi_utils/models/tflite_models',
        'wizzi_utils/models/test',
    ],
    version='7.0.11',
    license='MIT',  # https://help.github.com/articles/licensing-a-repository
    description='Handy Tools for Developers',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Gilad Eini',
    author_email='giladEini@gmail.com',
    url='https://github.com/2easy4wizzi/2021wizzi_utils',  # link to github
    download_url='https://github.com/2easy4wizzi/2021wizzi_utils/archive/refs/tags/v_7.0.11.tar.gz',
    keywords=[  # Keywords that define your package best
        'misc tools',
        'common algorithms',
        'coreset tools',
        'json tools',
        'open cv tools',
        'pyplot tools',
        'socket tools',
        'torch tools',
    ],
    install_requires=[
        'datetime',
        'typing',
        'numpy',
        'psutil',
        'matplotlib',
        'pip'
    ],
    classifiers=[
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3.6'
    ],
    platforms='windows',
)
