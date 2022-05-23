"""
Packaging script for PyPI.
"""
import sys, os, os.path, json, setuptools

home = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(home, 'python'))
from bedspread import __version__

def _refresh_grammar():
	folder = os.path.join(home, 'python', 'bedspread')
	src = os.path.join(folder, "grammar.md")
	dst = os.path.join(folder, "grammar.automaton")
	if os.path.exists(src):
		if (not os.path.exists(dst)) or (os.stat(dst).st_mtime < os.stat(src).st_mtime):
			from boozetools.macroparse.compiler import compile_file
			tables = compile_file(src, method='LR1')
			with open(dst, 'w') as ofh:
				json.dump(tables, ofh, separators=(',', ':'), sort_keys=True)
	else:
		assert os.path.exists(dst)
	
_refresh_grammar()

setuptools.setup(
	name='bedspread',
	author='Ian Kjos',
	author_email='kjosib@gmail.com',
	version=__version__,
	packages=['bedspread', ],
	package_dir = {'': 'python'},
	package_data={
		'bedspread': ['grammar.automaton',],
	},
	license='MIT',
	description='Bed Spread: an Expression-Oriented Code-in-Database System',
	long_description=open('README.md').read(),
	long_description_content_type="text/markdown",
	url="https://github.com/kjosib/mistake",
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
		"Development Status :: 2 - Pre-Alpha",
		"Intended Audience :: Developers",
		"Intended Audience :: Education",
		"Topic :: Software Development :: Interpreters",
		"Topic :: Software Development :: Libraries",
		"Topic :: Education",
		"Environment :: Console",
    ],
	python_requires='>=3.7',
	install_requires=[
		'booze-tools>=0.5.2',
	]
)