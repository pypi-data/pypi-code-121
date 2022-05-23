import os
import setuptools


def get_version():
    version = os.getenv('CI_COMMIT_TAG')
    if version is None:
        return 'no_version'
    else:
        return version


project_urls = {
    'ReadTheDoc': 'https://riffard.gitlab.io/job_farmer/read_the_doc/',
    'PyLint': 'https://riffard.gitlab.io/job_farmer/lint/',
    'Coverage': 'https://riffard.gitlab.io/job_farmer/coverage/'
}


with open('requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(
    name='job_farmer',
    version=get_version(),
    author="Quentin Riffard",
    author_email="quentin.riffard@gmail.com",
    url="https://gitlab.com/riffard/job_farmer",
    packages=setuptools.find_packages(),
    license='GNU Affero General Public License v3.0',
    description='A simple job farmer for HPC platforms',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    scripts=["job_runner/job_runner"],
    project_urls=project_urls,
    install_requires=required
)
