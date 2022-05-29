from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='ifs_etc',
    version='0.0.6',
    description='exposure time calculator',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='linlin',
    author_email='linlin@shao.ac.cn',
    packages=find_packages(where="src"),
    install_requires=['pandas>=1.3.3',
                      'numpy>=1.20.2',
                      'h5py>=2.8.0',
                      'einops>=0.3.2',
                      'matplotlib>=3.0.2',
                      'astropy>=4.2.1',
                      'scipy>=1.1.0',
                      'extinction>=0.4.0'],
    package_dir={"": "src"},
    include_package_data=True,
    # exclude_package_data={"": ["README.md"]},
    python_requires='>=3',
)

