from setuptools import setup

with open('README.md', 'r') as oF:
	long_description=oF.read()

setup(
	name='format-oc',
	version='1.5.17',
	description='Format-OC is a system designed in several languages that uses JSON files to define documents and their allowed parameters to such a fine degree that almost no knowledge of databases is required to get a fully functional back-end, with admin functions, up and running.',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://ouroboroscoding.com/format-oc',
	project_urls={
		'Source': 'https://github.com/ouroboroscoding/format-oc-python',
		'Tracker': 'https://github.com/ouroboroscoding/format-oc-python/issues'
	},
	keywords=['data','format','database','db','sql','nosql'],
	author='Chris Nasr - Ouroboros Coding Inc.',
	author_email='chris@ouroboroscoding.com',
	license='Apache-2.0',
	packages=['FormatOC'],
	install_requires=['future'],
	test_suite='tests',
	zip_safe=True
)
