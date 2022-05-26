from setuptools import setup

setup(
    name="metayaml",
    version="0.27",
    author="Anton Tagunov",
    packages=["metayaml"],
    package_data={'': ['test_files/*.yaml']},
    url="https://bitbucket.org/atagunov/metayaml/",
    description="Enhancements of yaml format to support include and python expression",
    long_description=open('README.rst').read(),
    install_requires=['jinja2<=2.11.3', 'PyYAML', 'six', 'MarkupSafe<=2.0.1'],
    include_package_data=True,
    test_suite="metayaml.test",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Environment :: Other Environment",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules"]
)
