#  (C) Copyright IBM Corp. 2021.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from setuptools import setup, find_packages
import os

with open('VERSION', 'r') as f_ver:
    VERSION = f_ver.read()


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


# read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

extras_require = {
    "fl": [
        "tensorflow==2.4.4",
        "scikit-learn==0.23.2",
        "torch==1.7.1",
        "numpy==1.19.2",
        "pandas==1.3.4",
        "pytest==6.2.5",
        "pyYAML==5.4.1",
        "parse==1.19.0",
        "websockets==8.1",
        "jsonpickle==1.4.2",
        "requests==2.27.1",
        "scipy==1.6.3",
        "environs==9.5.0",
        "pathlib2==2.3.6",
        "diffprivlib==0.5.1",
        "numcompress==0.1.2",
        "psutil",
        "setproctitle",
        "tabulate==0.8.9",
        "lz4",
        "gym",
        "cloudpickle==1.3.0",
        "image==1.5.33",
        "ddsketch==1.1.2",
        "skorch==0.11.0",
    ],

    "fl-rt22.1": [
        "tensorflow==2.7.1",
        "scikit-learn==1.0.2",
        "torch==1.10.2",
        "numpy==1.20.3",
        "pandas==1.3.4",
        "pytest==6.2.5",
        "pyYAML==5.4.1",
        "parse==1.19.0",
        "websockets==10.1",
        "jsonpickle==1.4.2",
        "requests==2.27.1",
        "scipy==1.7.3",
        "environs==9.5.0",
        "pathlib2==2.3.6",
        "diffprivlib==0.5.1",
        "numcompress==0.1.2",
        "psutil",
        "setproctitle",
        "tabulate==0.8.9",
        "lz4",
        "gym",
        "cloudpickle==1.3.0",
        "image==1.5.33",
        "ddsketch==1.1.2",
        "skorch==0.11.0",
    ],

}


def retrieve_all_files_from_path_and_sub_paths(path):
    listOfFiles = list()
    for (dirpath, dirnames, filenames) in os.walk(path):
        listOfFiles += [os.path.join(dirpath, file) for file in filenames]

    return listOfFiles


with open('MANIFEST.in', 'a') as f:
    f.writelines([f"exclude {line}\n" for line in
                  retrieve_all_files_from_path_and_sub_paths('ibm_watson_machine_learning/tests')])

setup(
    name='ibm_watson_machine_learning',
    version=VERSION,
    python_requires='>=3.7',
    author='IBM',
    author_email='svagaral@in.ibm.com, kaganesa@in.ibm.com, vbmithun@in.ibm.com, amadeusz.masny1@ibm.com',
    description='IBM Watson Machine Learning API Client',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='Apache License, Version 2.0',
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Natural Language :: English',
                 'License :: OSI Approved :: BSD License',
                 'Programming Language :: Python :: 3.7',
                 'Programming Language :: Python :: 3.8',
                 'Programming Language :: Python :: 3.9',
                 'Operating System :: MacOS :: MacOS X',
                 'Operating System :: POSIX :: Linux',
                 'Operating System :: Microsoft :: Windows',
                 'Intended Audience :: Science/Research',
                 'Intended Audience :: Developers',
                 'Intended Audience :: Information Technology',
                 'Topic :: Software Development :: Libraries',
                 'Topic :: Software Development :: Libraries :: Python Modules',
                 'Topic :: Scientific/Engineering :: Artificial Intelligence',
                 'Topic :: Scientific/Engineering :: Information Analysis',
                 'Topic :: Internet'],
    keywords=["watson", "machine learning", "IBM", "Bluemix", "client", "API", "IBM Cloud"],
    url='http://ibm-wml-api-pyclient.mybluemix.net',
    packages=find_packages(),
    package_data={'': ['messages/messages_en.json']},
    install_requires=[
        'requests',
        'urllib3',
        'pandas<1.4.0,>=0.24.2',
        'certifi',
        'lomond',
        'tabulate',
        'packaging',
        "ibm-cos-sdk==2.11.*; python_version>='3.9'",
        "ibm-cos-sdk==2.7.*; python_version<'3.9'",
        'importlib-metadata'
    ],
    include_package_data=True,
    extras_require=extras_require,
)
