from setuptools import setup

setup(
    name="log_telegram",
    version="0.2",
    packages=["log_telegram"],
    url="https://github.com/kevinpita/log-telegram",
    license="BSD-3-Clause",
    author="Kevin Pita",
    description="Logging handler to send logs to Telegram",
    keywords=["telegram", "logging"],
    install_requires=["pyTelegramBotAPI"],
)
