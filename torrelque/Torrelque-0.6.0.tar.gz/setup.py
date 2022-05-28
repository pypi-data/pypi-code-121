from setuptools import setup


setup(
    name             = 'Torrelque',
    version          = '0.6.0',
    author           = 'saaj',
    author_email     = 'mail@saaj.me',
    packages         = ['torrelque'],
    package_data     = {'torrelque' : ['*.lua']},
    license          = 'LGPL-3.0-only',
    description      = 'Asynchronous Redis-backed reliable queue package',
    long_description = open('README.rst', 'rb').read().decode('utf-8'),
    platforms        = ['Any'],
    keywords         = 'python redis asynchronous job-queue work-queue',
    url              = 'https://heptapod.host/saajns/torrelque',
    project_urls     = {
        'Source Code'   : 'https://heptapod.host/saajns/torrelque',
        'Documentation' : 'https://torrelque.readthedocs.io/',
        'Release Notes' : 'https://torrelque.readthedocs.io/en/latest/history.html',
    },
    classifiers = [
        'Topic :: Software Development :: Libraries',
        'Framework :: AsyncIO',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Intended Audience :: Developers',
    ],
    install_requires = ['yaaredis >= 3.0.0, < 4'],
    extras_require   = {
        'test'   : ['asynctest < 0.14'],
        'manual' : ['sphinx >= 4, < 5'],
    },
)
