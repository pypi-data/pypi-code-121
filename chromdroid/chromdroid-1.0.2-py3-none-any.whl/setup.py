from setuptools import setup

setup(
    name="chromdroid",
    version="1.0.0",
    description="simple python module to control browser but for android",
    author="tovanduy",
    author_email="toduyit21@gmail.com",
    url="https://github.com/tovanduy/chromdroid",
    python_requires="~=3.7",
    package_dir={
                "chromdroid": "chromdroid",
                "chromdroid.webdriver": "chromdroid/webdriver"
    },
    packages=[
        "chromdroid",
        "chromdroid.webdriver",
        "chromdroid.webdriver.chrome",
        "chromdroid.webdriver.remote",
        "chromdroid.webdriver.common"
    ],
    include_package_data=True,
    install_requires=[""],
    zip_safe=False
)
