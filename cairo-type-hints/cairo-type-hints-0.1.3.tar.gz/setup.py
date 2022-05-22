from setuptools import setup, find_packages

setup(
    name="cairo-type-hints",
    version="0.1.3",
    author="Chris Baker",
    author_email="lxufimdu@pm.me",
    description="Generate type hints for Cairo lang",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/playmint/cairo-type-hints",
    packages=find_packages(),
    license="LICENSE",
    install_requires=["lark==1.1.2"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Environment :: MacOS X",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development"
    ],
    entry_points={"console_scripts": ["compile-cairo-type-hints = cairo_type_hints.console:main"]},
    package_data={"cairo_type_hints": ["cairo.ebnf"]},
    include_package_data=True
)
