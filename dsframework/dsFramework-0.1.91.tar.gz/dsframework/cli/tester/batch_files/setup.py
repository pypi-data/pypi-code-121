import atexit
import os
import shutil
import sys
from typing import List
from glob import glob
from setuptools import find_packages, setup
from setuptools.command.bdist_egg import bdist_egg
from setuptools.command.install import install

# Extract build type
build_type = ''
if sys.argv and len(sys.argv) > 1:
	build_type = sys.argv[2]
	index = sys.argv.index(sys.argv[2])
	sys.argv.pop(index)

# If a build folder exists, delete it
build_dir = './build/'
if os.path.isdir(build_dir):
	shutil.rmtree(build_dir)

main_project_path = os.getcwd()
with open(main_project_path + '/requirements_docker.txt') as f:
	required = f.read().splitlines()
# print('required', required)


def package_files(directory, exclude_dirs: List = None):
	paths = []
	for (path, directories, filenames) in os.walk(directory):
		if exclude_dirs and isinstance(exclude_dirs, list):
			for item in exclude_dirs:
				if item in directories:
					directories.remove(item)
		for filename in filenames:
			paths.append(os.path.join('../' + path, filename))
	return paths


def read(fname):
	return open(os.path.join(os.path.dirname(__file__), fname)).read()


project_name = '{name-your-service}'


class PostInstallCommand(install):
	"""Post-installation for installation mode."""
	def run(self):
		def _post_install():
			ext = '.whl'
			target_ext = '.zip'
			path = main_project_path + '/dist/'
			target_file_name = path + project_name + target_ext
			if os.path.exists(target_file_name):
				os.remove(target_file_name)
			fileName = os.path.basename(glob(path + "*" + ext)[0])
			target_file_name = path + project_name + target_ext
			os.rename(path + fileName, target_file_name)

		atexit.register(_post_install)
		install.run(self)


class PostInstallCommand2(bdist_egg):
	"""Post-installation for installation mode."""
	def run(self):
		def _post_install():
			ext = '.egg'
			target_ext = '.egg'
			path = main_project_path + '/dist/'
			target_file_name = path + project_name + target_ext
			if os.path.exists(target_file_name):
				os.remove(target_file_name)
			fileName = os.path.basename(glob(path + "*" + ext)[0])
			target_file_name = path + project_name + target_ext
			os.rename(path + fileName, target_file_name)

		atexit.register(_post_install)
		bdist_egg.run(self)


pipes = package_files('pipes', ['.dvc', 'py_signature_parser', '__pycache__'])

pipeline = package_files('pipeline', ['__pycache__'])
batch_files = package_files('batch_files', ['__pycache__'])
tester = package_files('tester', ['__pycache__'])
config = package_files('config')

packages = ['pipeline']
data = config + pipes + pipeline + batch_files + tester
if build_type == 'no_pipes':
	data = config + pipeline + batch_files + tester
	project_name += '_' + build_type
if build_type == 'pipes':
	packages = ['pipes']
	data = pipes
	project_name += '_' + build_type

setup(
	name=project_name,
	packages=packages,
	package_data={
		'': [
				'../__init__.py',
		] + data
	},
	# package_data={'': ['batch_config.json', 'cors_allowed_origins.json','.gitignore'] + extra_files + cloud_eval_extra_files + dsp_files},

	# package_data={'': ['config/batch_config.json']},
	include_package_data=True,
	install_requires=required,
	cmdclass={
		'install': PostInstallCommand,
		'bdist_egg': PostInstallCommand2
	}
)
# commands
# for test -  python setup.py pytest
# for build wheel -  python setup.py bdist_wheel
# for source dist -  python setup.py sdist
# for build -  python setup.py build
# for install -  python setup.py install
# for uninstall - python -m pip uninstall trex-batch
# for install - python -m pip install dist/trex-batch-0.1.0-py3-none-any.whl

# deploy to PyPI
# delete dist and build folders
# python setup.py bdist_wheel
# python setup.py sdist
# python setup.py build
# twine upload dist/*
'''
	use
	1. python setup.py install
	2. dsf-cli g model new_model_name
	3. twine check dist/*
	4. twine upload --repository-url https://pypi.org/legacy/ dist/*
	4. twine upload dist/*
	
	pip install dsframework --index-url https://pypi.org/simple

	how to use

	pip install dsframework
	
	dsf-cli generate project my-new-model
'''
