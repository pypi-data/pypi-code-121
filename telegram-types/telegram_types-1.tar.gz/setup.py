import re
from setuptools import setup, find_packages

with open('requirements.txt', encoding='utf-8') as r:
    requires = [i.strip() for i in r]

with open('telegram_types/__init__.py', encoding='utf-8') as f:
    version = re.findall(r'__version__ = \'(.+)\'', f.read())[0]


setup(
    name='telegram_types',
    version=version,
    description='',
    long_description='',
    long_description_content_type='text/markdown',
    url='https://github.com/telectron',
    download_url='https://github.com/telectron/telectron/releases/latest',
    author='Dan',
    author_email='dan@telectron.org',
    license='LGPLv3+',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet',
        'Topic :: Communications',
        'Topic :: Communications :: Chat',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks'
    ],
    keywords='telegram chat messenger mtproto api client library python',
    python_requires='~=3.6',
    packages=find_packages(),
    zip_safe=False,
    install_requires=requires,
)
