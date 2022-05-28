from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

with open('HISTORY.md') as history_file:
    HISTORY = history_file.read()

setup_args = dict(
    name='deeplib-ml',
    version='0.1.0',
    description='Library to train deep learning models using PyTorch',
    long_description_content_type="text/markdown",
    long_description=README + '\n\n' + HISTORY,
    license='MIT',
    packages=find_packages(),
    author='Jonathan Bergqvist',
    author_email='jonathan.bergqvist96@gmail.com',
    keywords=['PyTorch'],
    url='https://github.com/jbergq/deeplib',
    download_url='https://pypi.org/project/deeplib-ml/'
)

install_requires = [
    'torch>=1.11.0'
] 

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)
