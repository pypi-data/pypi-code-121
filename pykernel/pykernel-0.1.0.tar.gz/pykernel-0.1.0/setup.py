from setuptools import setup
setup(
    name="pykernel",
    version="0.1.0",
    description="Python & text Windows CMD Editior written with only native libaries",
    py_modules=["editor","TIME"],
    package_dir={"":"code"},
    url="https://github.com/coolnicecool/editor",
    author="Raleigh Priour",
    author_email="raleigh@1337maps.com"
)
#python setup.py build
#python setup.py sdist bdist_wheel
#twine upload dist/*