from setuptools import setup, find_packages


def readme():
	with open('./README.md') as f:
		return f.read()


setup(
	name='amazonian',
	version='2022.5.27',
	license='MIT',

	url='https://github.com/idin/amazonian',
	author='Idin',
	author_email='py@idin.ca',

	description='Python library for working with Amazon Web Services such as Redshift and S3',
	long_description=readme(),
	long_description_content_type='text/markdown',

	classifiers=[
		'Development Status :: 3 - Alpha',
		'Intended Audience :: Developers',
		'Programming Language :: Python :: 3 :: Only',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: 3.7',
		'Topic :: Software Development :: Libraries :: Python Modules'
	],

	packages=find_packages(exclude=["jupyter_tests", ".idea", ".git"]),
	install_requires=[
		'numpy', 'pandas', 'sqlalchemy', 'psycopg2-binary', 's3fs>=2022.2.0', 'urllib3>=1.26.8' #, 'pyspark', 'botocore'
		#'aiobotocore==1.3.3' #todo check if the new update to s3fs has solved the issue, if yes, remove this line
	],
	python_requires='~=3.6',
	zip_safe=False
)
