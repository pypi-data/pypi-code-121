import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="ogl",
    version="0.51",
    author_email='Humberto.A.Sanchez.II@gmail.com',
    description='External Pyut Graphical Shapes',
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/hasii2011/pyutgraphicalmodel",
    packages=[
        'miniogl',
        'ogl',
        'ogl.events',
        'ogl.preferences',
        'ogl.resources', 'ogl.resources.img', 'ogl.resources.img.textdetails',
        'ogl.sd',
    ],
    install_requires=['Deprecated', 'pyutmodel', 'wxPython'],
)
