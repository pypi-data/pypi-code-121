from distutils.core import setup
setup(
    name='dataUncert',
    packages=['dataUncert'],
    version='2.7',
    license='MIT',
    description='import data from .xlsx and .xls files. Use the data to perform calculation with uncertanties',
    author='Jacob Vestergaard',
    author_email='jacobvestergaard95@gmail.com',
    url='https://github.com/jacobv95/dataProcessing',
    download_url='https://github.com/jacobv95/dataUncert/archive/refs/tags/v2.0.tar.gz',
    keywords=['python', 'data processing', 'uncertanty'],
    install_requires=[            # I get to this in a second
        'numpy', 'scipy', 'openpyxl', 'xlrd'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',      # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',  # Specify which pyhton versions that you want to support
    ],
)
