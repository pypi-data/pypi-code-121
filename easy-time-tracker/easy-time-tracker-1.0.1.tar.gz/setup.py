from setuptools import setup
import os

base_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(base_dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

about = {}
with open(os.path.join(base_dir, 'easy_time_tracker', 'version.py'), 'r', encoding='utf-8') as f:
    exec(f.read(), about)

packages = [
    'easy_time_tracker',
    'easy_time_tracker/util'
]

package_data = {}

install_requires = [
    "pydantic~=1.9.0",
    "pandas~=1.1.5; python_version == '3.6'",
    "pandas~=1.3.5; python_version == '3.7'",
    "pandas~=1.4.0; python_version >= '3.8'",
    "openpyxl~=3.0.9"
]

entry_points = {
    'console_scripts': [
        'ett=easy_time_tracker.cli:cli'
    ],
}

tests_require = [
    'pytest',
]

setup(
    name=about['__title__'],
    version=about['__version__'],
    python_requires='>=3.6',
    description=about['__description__'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='',
    url=about['__url__'],
    project_urls={
        'Documentation': 'https://easy-time-tracker.readthedocs.io/en/latest/',
        'Source': 'https://github.com/btr1975/easy-time-tracker',
        'Tracker': 'https://github.com/btr1975/easy-time-tracker/issues',
    },
    author=about['__author__'],
    author_email=about['__email__'],
    license=about['__license__'],
    packages=packages,
    include_package_data=True,
    install_requires=install_requires,
    test_suite='pytest',
    tests_require=tests_require,
    zip_safe=False,
    entry_points=entry_points,
    package_data=package_data,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: BSD',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
