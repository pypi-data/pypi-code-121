import setuptools


def open_requirements(path):
    with open(path) as f:
        requires = [
            r.split('/')[-1] if r.startswith('git+') else r
            for r in f.read().splitlines()]
    return requires


with open('README.md') as file:
    readme = file.read()


with open('HISTORY.md') as file:
    history = file.read()

requires = open_requirements('requirements.txt')
tests_requires = open_requirements('extra_requirements/requirements-tests.txt')
doc_requires = open_requirements('extra_requirements/requirements-docs.txt')

setuptools.setup(name='pema',
                 version='0.5.0',
                 description='Peak matching for XENON simulations',
                 author='Joran Angevaare',
                 url='https://github.com/XENONnT/peakmatching',
                 long_description=readme + '\n\n' + history,
                 long_description_content_type="text/markdown",
                 setup_requires=['pytest-runner'],
                 install_requires=requires,
                 tests_require=requires+tests_requires,
                 extras_require={
                     'docs': doc_requires,
                 },
                 python_requires=">=3.8",
                 packages=setuptools.find_packages() + ['extra_requirements'],
                 package_dir={'extra_requirements': 'extra_requirements'},
                 package_data={'extra_requirements': ['requirements-docs.txt',
                                                      'requirements-tests.txt']},
                 scripts=['bin/pema_straxer',
                          'bin/pema_init.py',
                          ],
                 classifiers=[
                     'Development Status :: 4 - Beta',
                     'License :: OSI Approved :: BSD License',
                     'Natural Language :: English',
                     'Programming Language :: Python :: 3.8',
                     'Programming Language :: Python :: 3.9',
                     'Programming Language :: Python :: 3.10',
                     'Intended Audience :: Science/Research',
                     'Programming Language :: Python :: Implementation :: CPython',
                     'Topic :: Scientific/Engineering :: Physics',
                 ],
                 zip_safe=False)
