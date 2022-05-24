from setuptools import setup


with open('README.md', 'rb') as f:
    longdesc = f.read().decode().strip()


setup(
    setup_requires=[
        'setuptools_scm',
    ],

    use_scm_version={
        'write_to': 'inspiral_range/__version__.py',
    },

    name='inspiral_range',
    description="GW detector inspiral range calculation tools",
    long_description=longdesc,
    long_description_content_type='text/markdown',
    author='Jameson Graef Rollins',
    author_email='jameson.rollins@ligo.org',
    url='https://git.ligo.org/gwinc/inspiral_range',
    license='GPL-3.0-or-later',
    classifiers=[
        ('License :: OSI Approved :: '
         'GNU General Public License v3 or later (GPLv3+)'),
        'Natural Language :: English',
        'Programming Language :: Python',
    ],

    install_requires=[
        'astropy',
        'gpstime',
        'numpy',
        'pyyaml',
        'scipy',
    ],
    extras_require={
        'lal': 'lalsuite',
        'plot': 'matplotlib',
    },

    packages=[
        'inspiral_range',
        'inspiral_range.test',
    ],
    package_data={
        'inspiral_range.test': ['*.txt', '*.yaml'],
    },

    entry_points={
        'console_scripts': [
            'inspiral-range = inspiral_range.__main__:main',
        ],
    },
)
