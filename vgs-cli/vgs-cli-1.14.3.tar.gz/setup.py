import re
import setuptools

from glob import glob

setuptools.setup(
    name='vgs-cli',
    version=(re.compile(r".*__version__ = '(.*?)'", re.S).match(open('vgscli/_version.py').read()).group(1)),
    zip_safe=False,
    url='https://github.com/verygoodsecurity/vgs-cli',
    license='BSD',
    author='Very Good Security',
    author_email='dev@verygoodsecurity.com',
    description='VGS Client',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages('.', exclude=('tests', 'tests_integration', 'tests.*')),
    platforms='any',
    install_requires=[line.replace('\n', '') for line in open('requirements.txt').readlines()],
    data_files=[('vgscli', [
        *glob('vgscli/resource-templates/**/*.yaml', recursive=True),
        *glob('vgscli/validation-schemas/**/*.yaml', recursive=True),
    ])],
    setup_requires=['pytest-runner'],
    tests_require=[line.replace('\n', '') for line in open('test-requirements.txt').readlines()],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    include_package_data=True,
    entry_points='''
        [console_scripts]
        vgs=vgscli.vgs:cli
    '''
)
