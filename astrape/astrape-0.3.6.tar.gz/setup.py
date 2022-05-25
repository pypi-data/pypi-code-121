
import setuptools

# Reads the content of your README.md into a variable to be used in the setup below
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='astrape',                           # should match the package folder
    packages=['astrape'],                     # should match the package folder
    version='0.3.6',                                # important for updates
    license='MIT',                                  # should match your chosen license
    description='Astrape: A Fast Way to Organize and Deploy ML experiments.',
    long_description=long_description,              # loads your README.md
    long_description_content_type="text/markdown",  # README.md is of type 'markdown'
    author='Woosog Benjamin Chay',
    author_email='benchay1@gmail.com',
    url='https://github.com/benchay1999/astrape', 
    project_urls = {                                # Optional
        "Bug Tracker": "https://github.com/benchay1999/astrape/issues"
    },
    install_requires=['pytorch-lightning', 'torch', 'numpy', 'rich', 'sklearn', 'pandas', 'overrides', 'scipy', 'tensorflow', 'torchmetrics'],                  # list all packages that your package uses
    keywords=["pypi", "astrape", "machine learning", "pytorch lightning", "lightning", "pytorch-lightning"], #descriptive meta-data
    classifiers=[                                   # https://pypi.org/classifiers
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Documentation',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    py_modules = [
        "astrape.base.experiment_base",
        "astrape.base.model_base",
        "astrape.constants.astrape_constants",
        "astrape.exceptions.exceptions",
        "astrape.models.models_lightning",
        "astrape.models.model_buildingblocks",
        "astrape.utilities.dataloader_lightning",
        "astrape.utilities.utils_lightning",
        "astrape.utilities.utils",
        "astrape.experiment",
        "astrape.model_selection",
        "astrape.project"
    ],
    download_url="https://github.com/benchay1999/astrape/releases/tag/0.3.6.tar.gz",
)
