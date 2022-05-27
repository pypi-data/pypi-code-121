import setuptools

""" 
To document:
===========

To distribute:
=============
rm dist/*; python setup.py sdist --formats=gztar,zip
or
rm dist/*; python setup.py sdist bdist_wheel; python -m twine upload dist/* 

"""

setuptools.setup(
    name="dcclab",
    version="1.0.9",
    url="https://github.com/DCC-Lab/PyDCCLab",
    author="Daniel Côté, Gabriel Genest, Mathieu Fournier, Ludovick Bégin",
    author_email="dccote@cervo.ulaval.ca",
    description="A Python library to read, transform, manipulate images and manage databases",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    keywords='image analysis stack movies',
    packages=setuptools.find_packages(),
    install_requires=['keyring', 'sshtunnel', 'mysql-connector-python', 'requests', 'matplotlib','numpy','scikit-image','scipy','czifile >= 2019.6.18','tifffile','read-lif','opencv-python','xlrd','seaborn','imagecodecs','deprecated'],
    python_requires='>=3',
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.png'],
        "doc": ['*.html']
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        # Indicate who your project is intended for
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Education',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',

        'Operating System :: OS Independent'
    ],
)
