from setuptools import setup

setup(
    name='poseutils',
    version='0.3.5',    
    description='A simple package containing common essentials for pose based research',
    author='Saad Manzur',
    author_email='smanzur@uci.edu',
    license='LICENSE.txt',
    packages=['poseutils', 'poseutils.datasets', 'poseutils.datasets.unprocessed', 'poseutils.datasets.transformation', 'poseutils.datasets.processed'],
    install_requires=['numpy', 'tqdm'],
    project_urls={ 'Documentation': 'https://saadmanzur.github.io/PoseUtils' },
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)