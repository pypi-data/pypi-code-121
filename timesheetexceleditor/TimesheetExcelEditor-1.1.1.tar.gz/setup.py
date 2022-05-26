from setuptools import setup
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name='TimesheetExcelEditor',
    version='1.1.1',
    description='An application for modify excel timesheet',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/alaino95/TimesheetExcelEditor',
    license='MIT',
    author='Alessandro Laino',
    author_email='alessandrolaino1@gmail.com',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    packages=['TimesheetExcelEditor'],
    install_requires=["wxpython",
                      "openpyxl",
                      "icalendar",
                      "validators",
                      "python-dateutil"
                      ],
)
