import setuptools

setuptools.setup(
    name="diagnscls", # Replace with your own username
    version="0.0.1",
    author="cmg56",
    author_email="cmg5691@naver.com",
    description="diagnosis non-small cell lung cancer",
    url="https://github.com/cheymingyu/Biomarker",
    packages=setuptools.find_packages(),
    scripts=['diagnscls/start_with_bam.sh', 'diagnscls/start_with_fastq.sh'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.6',
)
