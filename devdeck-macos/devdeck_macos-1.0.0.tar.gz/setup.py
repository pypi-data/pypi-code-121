from setuptools import setup, find_packages
import os
import subprocess


def get_version():
    process = subprocess.Popen(["git", "describe", "--always", "--tags"], stdout=subprocess.PIPE, stderr=None)
    last_tag = process.communicate()[0].decode('ascii').strip()
    if '-g' in last_tag:
        return last_tag.split('-g')[0].replace('-', '.')
    else:
        return last_tag


with open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'requirements.txt'))) as f:
    install_reqs = f.read().splitlines()

setup(
    name='devdeck_macos',
    version=get_version(),
    description="DevDeck commands for interacting with a macOS system",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Marcus Crane',
    author_email='marcus@utf9k.net',
    url='https://github.com/marcus-crane/devdeck-macos',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_reqs
)
