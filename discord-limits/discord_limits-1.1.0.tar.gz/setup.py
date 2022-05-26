from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='discord_limits',
    packages=find_packages(include=['discord_limits']),
    version='1.1.0',
    description='Make requests API requests to Discord without having to worry about ratelimits.',
    author='ninjafella',
    license='MIT',
    install_requires=['aiolimiter==1.0.0', 'aiohttp==3.8.1'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ninjafella/discord-API-limits",
    python_requires=">=3.9"
)
