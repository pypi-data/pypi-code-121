from setuptools import setup, find_packages
import subprocess

git_command_result: subprocess.CompletedProcess = subprocess.run(
    ["git", "describe", "--tags"], capture_output=True, encoding="utf-8"
)
actual_version: str = git_command_result.stdout.strip("\n") or "1.0.1"

setup(
    name="LinuxServerStatsTelegramBot",
    version=actual_version,
    packages=find_packages(),
    url="",
    license="MIT",
    author="Juares Vermelho Diaz",
    author_email="j.vermelho@gmail.com",
    description="Telegram bot manager to show linux server stats",
    entry_points={
        "console_scripts": [
            "send_stats_by_telegram = LinuxServerStatsTelegramBot.cli:notify_server_stats",
            "start_bot = LinuxServerStatsTelegramBot.bot:main",
        ]
    },
    package_data={"": ["assets/*.webp"]},
    include_package_data=True,
    install_requires=[
        "apscheduler==3.6.3",
        "cachetools==4.2.2; python_version ~= '3.5'",
        "certifi==2022.5.18.1; python_version >= '3.6'",
        "charset-normalizer==2.0.12; python_version >= '3'",
        "click==8.1.3; python_version >= '3.7'",
        "croniter==1.3.5",
        "decorator==5.1.1; python_version >= '3.5'",
        "future==0.18.2; python_version >= '2.6' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "geocoder==1.38.1",
        "gps==3.19",
        "idna==3.3; python_version >= '3'",
        "pillow==9.1.1",
        "python-crontab==2.6.0",
        "python-dateutil==2.8.2; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "python-nmap==0.7.1",
        "python-telegram-bot==13.11",
        "pytz==2022.1",
        "pytz-deprecation-shim==0.1.0.post0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4, 3.5'",
        "ratelim==0.1.6",
        "requests==2.27.1; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4, 3.5'",
        "six==1.16.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "tornado==6.1; python_version >= '3.5'",
        "tzdata==2022.1; python_version >= '3.6'",
        "tzlocal==4.2; python_version >= '3.6'",
        "urllib3==1.26.9; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4' and python_version < '4'",
    ],
)
