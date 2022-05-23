from setuptools import setup

setup(
    name='zservices',
    packages=['zdynamodb', 'zdiscord', 'zrequests', 'zs3', 'zsftp'],
    package_dir={'zdynamodb': 'zdynamodb', 'zdiscord': 'zdiscord', 'zrequests': 'zrequests', 'zs3': 'zs3',
                 'zsftp': 'zsftp'},
    version='0.2.4',
    license='MIT',
    platforms='cross-platfom, platform-independent',
    description='ZFunds basic services',
    long_description='Dependencies: coming soon',
    author='Yogesh Yadav',
    author_email='yogesh@zfunds.in',
    url='https://github.com/ZFunds/zservices/',
    download_url='https://github.com/ZFunds/zservices/',
    keywords=['dynamodb', 'discord', 's3', 'requests', 'sftp'],
    install_requires=[
        'python-dotenv==0.19.2', 'boto3==1.21.17', 'requests==2.27.1', 'paramiko==2.10.4'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3.10',
    ],
)
