import setuptools


setuptools.setup(
    name="http-copy",
    version="1.0",
    license="MIT",
    description="A simple tool to 'copy' local file or directory to a remote url (recursively) through http.",
    author='Kang-Min Yoo',
    author_email='kangmin.yoo@gmail.com',
    url='https://github.com/kaniblu/http-copy',
    entry_points={
        "console_scripts": [
            "http-copy = http_copy:main"
        ]
    },
    py_modules=[
        "http_copy"
    ],
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    platforms=[
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
    ],
    install_requires=[line.rstrip() for line in open("requirements.txt")],
)