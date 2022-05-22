import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='dropbox-updater',
    version='1.0.6',
    author='Pradish Bijukchhe',
    author_email='pradishbijukchhe@gmail.com',
    description='Module to update python script using dropbox api',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/sandbox-pokhara/dropbox-updater',
    project_urls={
        'Bug Tracker': 'https://github.com/sandbox-pokhara/dropbox-updater/issues',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    package_dir={'': '.'},
    packages=setuptools.find_packages(where='.'),
    python_requires='>=3.6',
    install_requires=['requests', 'requests-futures'],
)
