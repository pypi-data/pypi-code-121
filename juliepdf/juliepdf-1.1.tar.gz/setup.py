# This setup file is where important aspects of the package / project are configured.

import setuptools
# One of the tools (setuptools, twine, wheel) installed for publishing package.

from pathlib import Path

setuptools.setup(
    name="juliepdf",  # name of package
    version=1.1,  # version of package being created and published
    long_desciption=Path("README.md").read_text(),  # Reading from README.md
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=["test", "data"])
    # 1. 'find_packages' method automatically finds all the modules/source_code/python_files inside this 'JULIEPDF' Dir.
    # 2. 'exclude' keyword is used to ask 'find_packages' method to exclude the two folders 'test' and 'data' as they
    # do not contain any source code.
)
