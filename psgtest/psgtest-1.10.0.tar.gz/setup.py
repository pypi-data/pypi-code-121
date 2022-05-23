import setuptools

def readme():
    try:
        with open('README.md') as f:
            return f.read()
    except IOError:
        return ''


setuptools.setup(
    name="psgtest",
    version="1.10.0",
    author="PySimpleGUI",
    author_email="PySimpleGUI@PySimpleGUI.org",
    description="Run your Python programs, capture the output, using your choice of interpreters",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/PySimpleGUI/psgtest",
    packages=['psgtest'],
    install_requires=['PySimpleGUI>=4.55.1', 'psutil'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Topic :: Multimedia :: Graphics",
        "Operating System :: OS Independent"
    ],
    package_data={"":["*.ico"]},
    entry_points={
        'gui_scripts': [
            'psgtest=psgtest.psgtest:main'
        ],
    },
)
