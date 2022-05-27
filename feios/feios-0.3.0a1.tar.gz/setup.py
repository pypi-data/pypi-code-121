import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="feios",
    version="0.3.0a1",
    author="fyc",
    author_email="fycsfls_winter@126.com",
    description="The feios main module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/devoter-fyc/fei-ros",
    project_urls={
        "Bug Tracker": "https://github.com/devoter-fyc/fei-ros/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha"
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.5",
    install_requires=['feios-utils>=0.2.0b3']
)
