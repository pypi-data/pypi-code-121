from setuptools import setup, find_packages

__version__ = '0.1'

setup(
    name="pynextflow",
    version=__version__,
    packages=find_packages(),
    author='Jordi Deu-Pons',
    description="Nextflow pipelines with Python",
    long_description="""
## Description
Create pipelines adding @nf.process and @nf.workflow decorators 
and run them with Nextflow from python.

## Example
```
import pynextflow as nf

@nf.process(echo=True)
def hello(cheers: str) -> nf.bash:
    return f"echo {cheers}"

with nf.Nextflow():
    hello(["hola", "hello", "ciao"])
```
""",
    long_description_content_type="text/markdown",
    license="MPL-2",
    keywords=["pipeline", "workflow"],
    install_requires=[],
    classifiers=[]
)
