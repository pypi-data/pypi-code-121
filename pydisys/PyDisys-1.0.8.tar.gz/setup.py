from setuptools import setup

setup(
    name='PyDisys',
    version='1.0.8',    
    description='Disys library for calibration',
    author='NF',
    package_dir={'': 'src'},
    py_modules=['Disys_calib','Disys_DL'],
    install_requires=['matplotlib>=3.5.1', 
    'mvtec_halcon>=21050.0.0', 'numpy>=1.21.2', 
    'pandas>=1.3.4', 'Pillow>=9.1.0',
     'pyrenn>=0.1', 'scikit_learn>=1.0.2','split-folders>=0.5.1']
)

##python setup.py bdist_wheel
##python setup.py sdist

## Delete prev version
##twine upload dist/*

