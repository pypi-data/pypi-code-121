from setuptools import setup

setup(
    name='normflow',
    version='0.1.0',
    packages=['normflow', 'normflow.hli', 'normflow.flows', 'normflow.common', 'normflow.splits', 'normflow.couplings',
              'normflow.transforms', 'normflow.transforms.permutations'],
    url='https://github.com/LarsKue/normflow',
    license_files=("LICENSE",),
    author='Lars Kuehmichel',
    author_email='lars.kuehmichel@stud.uni-heidelberg.de',
    description='A Python Package for Normalizing Flows'
)
