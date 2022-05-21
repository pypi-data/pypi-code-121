
import os
from setuptools import setup, find_packages
from importlib.machinery import SourceFileLoader

version = (
    SourceFileLoader("modelify.version", os.path.join("modelify", "version.py")).load_module().VERSION
)

setup(
    name='modelify',
    version=version,
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='New Version of MLOps Platforms.',
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),
    install_requires=['numpy',"pandas", "cloudpickle", 'python-multipart', 'jinja2', 'Pillow', 'onnxmltools','onnxruntime','skl2onnx','requests-toolbelt','tf2onnx', 'pydantic','tqdm', 'python-dotenv', "pyngrok", "nest-asyncio", "click", "uvicorn", "fastapi"],
    author='Muzaffer Senkal',
    author_email='info@modelify.ai',
    keywords=['mlops', 'machine learning', 'model deployment', 'deploy model', 'data science', 'computer vision'],
    entry_points = {
        'console_scripts': [
            'modelify = modelify.cli:cli'
        ]
    },
    include_package_data=True,
     package_data = {
        '': ['*.html', '*.css'],
    },
)
