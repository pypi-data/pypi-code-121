import os
import setuptools

package_name = 'd3m_interface'


def read_readme():
    with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf8') as file:
        return file.read()


def read_version():
    module_path = os.path.join(package_name, '__init__.py')
    with open(module_path) as file:
        for line in file:
            parts = line.strip().split(' ')
            if parts and parts[0] == '__version__':
                return parts[-1].strip("'")

    raise KeyError('Version not found in {0}'.format(module_path))


long_description = read_readme()
version = read_version()

setuptools.setup(
    name=package_name,
    version=version,
    author='Roque Lopez, Remi Rampin, Sonia Castelo',
    author_email='rlopez@nyu.edu, remi.rampin@nyu.edu, s.castelo@nyu.edu',
    maintainer='Roque Lopez, Remi Rampin',
    maintainer_email='rlopez@nyu.edu, remi.rampin@nyu.edu',
    description='Library to use D3M AutoML Systems',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/ViDA-NYU/d3m/d3m_interface',
    packages=setuptools.find_packages(),
    license='Apache-2.0',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'd3m',
        'd3m-automl-rpc',
        'pandas>=1.1.3,<=1.3.4',
        'numpy',
        'scikit-learn',
        'lime>=0.2,<0.3',
        'pipelineprofiler>=0.1,<2',
        'datamart_profiler>=0.9',
        'data-profile-viewer>=0.2.7,<3',
        'visual-text-explorer>=0.1,<2',
    ],
    python_requires='>=3.6',
    include_package_data=True
)
