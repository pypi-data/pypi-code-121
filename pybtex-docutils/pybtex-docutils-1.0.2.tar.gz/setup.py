from setuptools import setup
import io


def readfile(filename):
    with io.open(filename, encoding="utf-8") as stream:
        return stream.read().split("\n")


doclines = readfile("README.rst")[5:]  # skip title and badges
requires = readfile("requirements.txt")
version = readfile("VERSION")[0].strip()

setup(
    name='pybtex-docutils',
    version=version,
    url='https://github.com/mcmtroffaes/pybtex-docutils',
    download_url='http://pypi.python.org/pypi/pybtex-docutils',
    license='MIT',
    author='Matthias C. M. Troffaes',
    author_email='matthias.troffaes@gmail.com',
    description=doclines[0],
    long_description="\n".join(doclines[2:]),
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Text Editors :: Text Processing',
        'Topic :: Text Processing :: Markup :: XML'
    ],
    platforms='any',
    packages=['pybtex_docutils'],
    package_dir={'': 'src'},
    package_data={'pybtex_docutils': ['py.typed']},
    install_requires=requires,
    entry_points={
        'pybtex.backends': [
            'docutils = pybtex_docutils:Backend',
        ]
    },
    python_requires='>=3.6',
)
