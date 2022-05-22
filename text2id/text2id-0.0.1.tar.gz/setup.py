from setuptools import find_packages, setup

readme = open('README.md').read()

VERSION = '0.0.1'

requirements = [
    'inflect',
]

setup(
    # Metadata
    name='text2id',
    version=VERSION,
    author='Andrey Anufriev',
    author_email='a.a.egorovich@gmail.com',
    url='https://github.com/andreyanuf/text2id',
    description='Text converter for text to speech tasks.',
    long_description=readme,
    long_description_content_type='text/markdown',
    license='MIT',
    packages=find_packages(),
    package_data={'': ['text2id/data/cmudict']},
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    # Classifiers
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)