import setuptools

setuptools.setup(
    name="vupysolr",
    version="0.1.7",
    author="Donatus Herre",
    author_email="donatus.herre@slub-dresden.de",
    description="Access Solr stored VuFind records.",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    license="GPLv3",
    url="https://github.com/herreio/vupysolr",
    packages=["vupysolr"],
    install_requires=["pysolr", "pymarc", "python-dateutil", "requests"],
    entry_points={
      'console_scripts': ['vupysolr = vupysolr.__main__:main'],
    },
)
