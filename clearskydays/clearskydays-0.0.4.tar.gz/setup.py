from setuptools import setup, find_packages
 
classifiers = [
	'License :: OSI Approved :: MIT License',
	'Programming Language :: Python :: 3',
	'Programming Language :: Python :: 3.7',
]
 
setup(
	name='clearskydays',
	version='0.0.4',
	description='A simple Python module that determines clear sky days based on solar ultraviolet radiation measurements.',
	long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
	#long_description=open('README.rst').read() + '\n\n' + open('CHANGELOG.rst').read(),
	long_description_content_type='text/plain',
	url='',  
	author='Abel Delgado Villalba',
	author_email='adelgado@pol.una.py',
	license='MIT', 
	classifiers=classifiers,
	keywords='clear sky days, solar ultraviolet radiation', 
	packages=find_packages(),
	install_requires=['numpy', 'pandas'] 
)


