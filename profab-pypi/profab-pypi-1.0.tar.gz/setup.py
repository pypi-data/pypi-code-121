import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description_ = fh.read()
requirements = ['wget==3.2', 'tqdm==4.63.0','requests==2.27.1', 'numpy==1.21.2', 'scikit-learn==1.0.1']
setuptools.setup(
    name='profab-pypi',
    version='1.0',
    author='samet ozdilek',
    author_email='oz.samet.473@gmail.com',
    description='Installation of Package',
    long_description= long_description_,
    long_description_content_type="text/markdown",
    url='https://github.com/Sametle06/ProFAB',
    project_urls = {
        "Bug Tracker": "https://github.com/Sametle06/ProFAB/issues"
    },
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7",
)
