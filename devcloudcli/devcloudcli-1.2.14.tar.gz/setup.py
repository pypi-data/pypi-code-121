from setuptools import setup,find_packages
import os

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join(path, filename))
    print("Paths:", paths)
    return paths

extra_files = package_files('src/scripts')

setup(
    name='devcloudcli',
    version='1.2.14',
    description='AN Interactive CLI for Intel DevCloud Bench',    
    license='Proprietary - Intel',
    author="karthik kumaar",
    author_email='karthikx.kumaar@intel.com',
    #packages=['dc_cli','dc_cli.src'],
    packages=find_packages('dc_cli'),    
    package_dir={'': 'dc_cli'},
    package_data={'': extra_files
},
    include_package_data=True,
    keywords='dc project',
    install_requires=[
          'cmd2',
          'pexpect',
      ],
    entry_points={"console_scripts":["dc_cli = src.dc_cli:main"]},
    python_requires=">=3.6",
)
