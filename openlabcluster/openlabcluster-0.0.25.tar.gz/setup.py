# from setuptools import setup, find_packages
#
VERSION = '0.0.25'
DESCRIPTION = 'OpenLabCluster'
LONG_DESCRIPTION = open('README.md', 'r').read()
REQUIREMENTS = [i.strip() for i in open("requirements.txt").readlines()]
#
# # Setting up
# setup(
#        # the name must match the folder name 'verysimplemodule'
#         name="openlabcluster",
#         version=VERSION,
#         author="Jingyuan Li",
#         author_email="<jingyli6@uw.edu>",
#         project_urls = {
#             'GitHub': 'https://github.com/christincha/IC_GUI'
#         },
#         description=DESCRIPTION,
#         long_description=LONG_DESCRIPTION,
#         long_description_content_type='text/markdown',
#         packages=find_packages(),
#         install_requires=REQUIREMENTS, # add any additional packages that
#         include_package_data=True,
#         # needs to be installed along with your package. Eg: 'caer'
#         # entry_points='''
#         #     [gui_scripts]
#         #     openlabcluster=openlabcluster.gui.launch_script_pythonw:run
#         # ''',
#         keywords=['python', 'first package'],
#         classifiers= [
#             "Development Status :: 3 - Alpha",
#             "Intended Audience :: Education",
#             "Programming Language :: Python :: 2",
#             "Programming Language :: Python :: 3",
#             "Operating System :: MacOS :: MacOS X",
#             "Operating System :: Microsoft :: Windows",
#         ]
#
# )


"""
DeepLabCut2.0-2.2 Toolbox (deeplabcut.org)
© A. & M. Mathis Labs
https://github.com/DeepLabCut/DeepLabCut
Please see AUTHORS for contributors.
https://github.com/DeepLabCut/DeepLabCut/blob/master/AUTHORS
Licensed under GNU Lesser General Public License v3.0
"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="openlabcluster",
    version=VERSION,
    author="Jingyuan Li",
    author_email="jingyli6@uw.edu",
    description="OpenLabCluster",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/shlizee/OpenLabCluster",
    install_requires=REQUIREMENTS,
    extras_require={
        "gui": ["wxpython<4.1"],
    },
    packages=setuptools.find_packages(),
    include_package_data=True,
    keywords=['python', 'first package'],
    classifiers= [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    entry_points='''
        [gui_scripts]
        openlabcluster=openlabcluster.gui.launch_script_pythonw:run
    ''',
)