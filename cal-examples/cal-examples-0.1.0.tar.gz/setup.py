import re, ast
from setuptools import setup, find_packages


def version(name):
    _re = re.compile(r'__version__\s+=\s+(.*)')
    with open(f'{name}/__init__.py', 'rb') as f:
        return str(ast.literal_eval(_re.search(f.read().decode('utf-8')).group(1)))


setup(
    name='cal-examples',
    version=version('cal_examples'),
    author='Kye-Hyeon Kim',
    author_email='khkim@superb-ai.com',
    packages=find_packages(),
    install_requires=[
        'tensorflow>=2.3.1',
        'numpy>=1.18.5',
        'pillow>=8.1.2',
        'matplotlib>=3.3.4',
    ],
    extras_require={},
    package_data={},
)
