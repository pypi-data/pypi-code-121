from setuptools import setup
import labcsv
with open('README.md', 'r', encoding='utf-8') as fp:
    readme = fp.read()
LONG_DESCRIPTION = readme
LONG_DESCRIPTION_CONTENT_TYPE = 'text/markdown'
setup(
    name="labcsv",
    author="sn-10",
    url="https://github.com/s-n-1-0/labcsv.py",
    download_url="https://github.com/s-n-1-0/labcsv.py",
    version=labcsv.__version__,
    description="Get data column by column from the CSV file export by lab.js. Use Pandas.",
    install_requires=["numpy>=1.20.3", "pandas>=1.3.4",],
    packages=["labcsv"],
    license="MIT",
    keywords= ["labjs","lab.js"],
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown"
)