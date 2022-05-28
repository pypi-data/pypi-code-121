from setuptools import setup

setup(
    name='jija',
    version='0.0.5',
    description='',
    packages=[
        'jija',
        'jija.database',
        'jija.forms',
        'jija.commands',
        'jija.utils',
        'jija.middlewares',
        'jija.config'
    ],
    author='Kain',
    author_email='kainedezz.2000@gmail.com',
    zip_safe=False,

    install_requires=[
        'aiohttp==3.8.1',
        'aerich',
        'tortoise-orm==0.19.1',
        'asyncpg==0.25.0',
        'cryptography',
        'watchdog',
        'aiohttp_session[secure]',
    ]
)
