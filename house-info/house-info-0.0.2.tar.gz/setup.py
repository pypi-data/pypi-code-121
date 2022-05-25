from setuptools import setup, find_packages

setup(
    name="house-info",
    version="0.0.2",
    description="공공 주택 공고 정보 수집",
    author="Jungminchae",
    author_email="minggae0629@gmail.com",
    url="https://github.com/c2-house/house-info",
    install_requires=["selenium", "requests", "beautifulsoup4", "pandas"],
    include_package_data=True,
    packages=find_packages(),
    keywords=["house-info"],
    python_requires=">=3",
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
