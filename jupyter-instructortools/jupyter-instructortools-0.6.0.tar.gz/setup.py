import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="jupyter-instructortools",
    version="0.6.0",
    description="Useful tools for instructors creating Jupyter notebook templates.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JupyterPhysSciLab/jupyter-instructortools",
    author="Jonathan Gutow",
    author_email="jgutow@new.rr.com",
    license="GPL-3.0+",
    packages=setuptools.find_packages(),
    package_data={'InstructorTools': ['javascript/*.js']},
    include_package_data=True,
    install_requires=[
        # 'python>=3.6',
        'jupyter>=1.0.0',
        'notebook>=6.4.10',
        'jupyter-datainputtable>=0.7.5',
        'JPSLUtils',
        'JPSLMenus'
        #'pandas>=0.22.0'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: JavaScript',
        'Operating System :: OS Independent'
    ]
)
