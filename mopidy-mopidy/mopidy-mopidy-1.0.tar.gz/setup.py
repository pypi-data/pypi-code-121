from setuptools import setup

setup(
    name='mopidy-mopidy',
    version='1.0',
    description='Mopidy satellite extension',
    description_file='README.md',
    url='https://github.com/stffart/mopidy-mopidy',
    author='stffart',
    author_email='stffart@gmail.com',
    license='GPLv3',
    packages=['mopidy_mopidy'],
    package_dir={'mopidy_mopidy':'mopidy_mopidy'},
    package_data={'mopidy_mopidy':['ext.conf']},
    install_requires=[],
    entry_points={
        'mopidy.ext': [
            'mopidy_mopidy = mopidy_mopidy:Extension',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)

