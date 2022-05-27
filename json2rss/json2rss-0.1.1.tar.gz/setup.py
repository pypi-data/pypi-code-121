from setuptools import setup, find_packages

setup(
    name='json2rss',
    version='0.1.1',
    description='Json2RSS converter (supports JsonFeed input)',
    author='proteus',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    python_requires='>=3',
    entry_points='''
        [console_scripts]
        json2rss=json2rss:main
    ''',
    license='GPLv3',
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities"
    ]
)
