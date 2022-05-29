#!/usr/bin/env python
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()
    requirements = [req.replace('==', '>=') for req in requirements]


setuptools.setup(
    name='pollination-honeybee-vtk',
    author='ladybug-tools',
    author_email='info@ladybug.tools',
    maintainer='Devang, ladybug-tools',
    maintainer_email='devang@ladybug.tools, info@ladybug.tools',
    packages=setuptools.find_namespace_packages(
        include=['pollination.*'], exclude=['tests', '.github']
    ),
    install_requires=requirements,
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    url='https://github.com/pollination/honeybee-vtk',
    project_urls={
        'icon': 'https://raw.githubusercontent.com/pollination/honeybee-vtk/master/assets/logo/vtk.png',
        'docker': 'https://hub.docker.com/r/ladybugtools/honeybee-vtk'
    },
    description='Honeybee vtk plugin for Pollination.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords='honeybee, vtk, hbjson, ladybug-tools',
    license='PolyForm Shield License 1.0.0, https://polyformproject.org/wp-content/uploads/2020/06/PolyForm-Shield-1.0.0.txt',
    zip_safe=False
)
