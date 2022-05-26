from setuptools import setup
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='AlgorithmLib',
    version='3.0.18',
    packages=setuptools.find_packages(),
    url='https://github.com/pypa/sampleproject',
    license='MIT',
    author=' MA JIANLI',
    author_email='majianli@corp.netease.com',
    description='audio algorithms to compute and test audio quality of speech enhencement',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
    'numpy',
    'wave',
    'matplotlib',
    'datetime',
    'scipy',
    'pystoi',
    'paramiko',
    'moviepy',
    'torch',
    'librosa',
    'requests',
    'pandas',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    data_files=[
                ('', ['algorithmLib/DLLs/p563.dll']),
                ('', ['algorithmLib/DLLs/resampler.dll']),
                ('', ['algorithmLib/DLLs/g160.dll']),
                ('', ['algorithmLib/DLLs/VQTDll.dll']),
                ('', ['algorithmLib/DLLs/cygwin1.dll']),
                ('', ['algorithmLib/DLLs/peaqb.exe']),
                ('', ['algorithmLib/DLLs/PY_PESQ.dll']),
                ('', ['algorithmLib/DLLs/matchsig.dll']),
                ('', ['algorithmLib/DLLs/snr_music.dll']),
                ('', ['algorithmLib/DLLs/snr_transient.dll']),
                ('', ['algorithmLib/DLLs/time_align.dll']),
                ('', ['algorithmLib/DLLs/agcDelay.dll']),
                ('', ['algorithmLib/DLLs/attackrelease.dll']),
                ('', ['algorithmLib/DLLs/gaintable.dll']),
                ('', ['algorithmLib/DLLs/musicStability.dll']),
                ('', ['algorithmLib/DLLs/matchsig_aec.dll']),
                ('', ['algorithmLib/DLLs/ERLE_estimation.dll']),
                ('', ['algorithmLib/DLLS/SC_res_retrain_220316_185754125621__ep_007.tar']),
                ],

    python_requires='>=3.7',
)



