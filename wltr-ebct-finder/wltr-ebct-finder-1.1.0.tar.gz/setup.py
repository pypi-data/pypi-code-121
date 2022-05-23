import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


requirements = [
    'beautifulsoup4',
    'requests',
    'unidecode',
]

setuptools.setup(
    name="wltr-ebct-finder",
    version="1.1.0",
    author="Walter Avelino",
    author_email="walter.avelin@gmail.com",
    description="API para consulta de endereço e CEP",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/walteravelino/wltr-ebct-finder",
    packages=[
        'wltr_ebct_finder',
    ],
    package_dir={
        'wltr_ebct_finder': 'wltr_ebct_finder',
    },
    install_requires=requirements,
    keywords='cep endereco correios ebct api busca',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Natural Language :: Portuguese',
        'Intended Audience :: Developers',
    ],
)
