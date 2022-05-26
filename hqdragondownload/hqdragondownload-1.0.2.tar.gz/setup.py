from setuptools import setup

setup(
    name = 'hqdragondownload',
    version = '1.0.2',
    author = 'MrPowerUp',
    scripts=['./hqdragon/main'],
    author_email = 'gustavohenrique8282@hotmail.com',
    packages = ['hqdragon'],
    description = 'CLI para baixar hqs no site.',
    long_description = 'CLI para baixar hqs no site.',
    url = 'https://github.com/MrPowerUp82/hqdragondownload',
    project_urls = {
        'Código fonte': 'https://github.com/MrPowerUp82/hqdragondownload',
    },
    license = 'MIT',
    keywords = 'CLI hqdragon HQ',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Portuguese (Brazilian)',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Internationalization',
        'Topic :: Scientific/Engineering :: Physics'
    ],
    install_requires=['lxml==4.8.0','requests==2.27.1','fpdf==1.7.2']
)