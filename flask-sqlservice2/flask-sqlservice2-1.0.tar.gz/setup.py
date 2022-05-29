from setuptools import setup

setup(
    name='flask-sqlservice2',
    # should match the package folder
    packages=['flasksqlservice2'],
    version='1.0',
    author='Ahmad Yahia',
    description='Flask extension for integration with sqlservice package > 2.0',
    keywords='flask, sql, extensions, sqlservice',
    python_requires='>=3.7, <4',
    install_requires=['sqlservice', 'flask'],
    classifiers=[                                   
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Documentation',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ]
)
