from setuptools import setup
from pathlib import Path

this_dir = Path(__file__).parent
long_desc = (this_dir / 'README.md').read_text()

setup(
	name='pytest-assertcount',
	version='0.0.2',
	description='Plugin to count actual number of asserts in pytest',
	longdescription=long_desc,
	classifiers=[
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python',
		'Programming Language :: Python :: 3',
		'Topic :: Software Development :: Testing',
		'Framework :: Pytest',
	],
	keywords='pytest,plugin,assert',
	author='Roman Joeres',
	license='MIT',
	author_email='romanjoeres@gmail.com',
	py_modules=['pytest_assertcount'],
	url='https://github.com/Old-Shatterhand/pytest-assertcount',
	platforms='any',
	python_requires='>=3.0',
	install_requires=[
		'pytest>=5.0.0',
	],
	entry_points={
		'pytest11': ['toolbox = pytest_assertcount'],
	},
)