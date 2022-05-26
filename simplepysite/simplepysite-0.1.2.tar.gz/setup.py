from setuptools import setup

setup(  name='simplepysite',
        version='0.1.2',
        description='Simple static site generator',
        long_description=open('README.md', 'r').read(),
        long_description_content_type='text/markdown',
        packages=['simplepysite'],
        author = 'Rocco Panella',
        author_email='panella.rocco@gmail.com',
        license='MIT',
        install_requires=[
            'markdown',
        ],
        url='https://github.com/paloblanco/simplepysite',
        zip_safe=False)