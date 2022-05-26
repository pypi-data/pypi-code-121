from distutils.core import setup

setup(
    name='Lshengpackage',  # How you named your package folder (MyLib)
    packages=['Lshengpackage'],  # Chose the same as "name"
    version='0.2.9',  # Start with a small number and increase it with every change you make
    license='MIT',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description='个人自动化爬虫开源学习',  # Give a short description about your library
    author='Lsheng0-0',  # Type in your name
    author_email='1522833718@qq.com',  # Type in your E-Mail
    url='https://github.com/Lsheng0-0/package',  # Provide either the link to your github or to your website
    download_url='https://github.com/Lsheng0-0/package',  # I explain this later on
    keywords=['游戏', '自动化', '爬虫'],  # Keywords that define your package best
    install_requires=[  # I get to this in a second
        'numpy',
        'aircv',
        'Pillow',
        'opencv-python',
        'pywin32',
        'requests',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3',  # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.9',
    ], )
