import setuptools
import versioneer

with open("README.md", "r") as fh:
    long_description = fh.read()

try:
    with open('requirements.txt') as f:
        requirements = f.read().splitlines()
except FileNotFoundError:
    with open('gdrive.egg-info/requires.txt') as f:
        requirements = f.read().splitlines()

setuptools.setup(
    name="gdrive",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="kiemlicz",
    author_email="stanislaw.dev@gmail.com",
    description="Google Drive simple client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kiemlicz/gdrive",
    install_requires=requirements,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
