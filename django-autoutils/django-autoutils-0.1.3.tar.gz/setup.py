"""
Setup auto_utils
"""
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

packages = [
    'django_autoutils',
]

install_requires = [
    "Django>=4.0",
    "djangorestframework>=3.0",
    "autoutils>=0.1",
    "Pygments>=2.0",
    "django-admin-autocomplete-filter>=0.1",
    "Markdown>=3.0",
    "Pillow>=9.0",
    "django-admin-list-filter-dropdown>=1.0",
]

setup(
    name="django-autoutils",
    version="0.1.3",
    author="Reza Zeiny",
    author_email="rezazeiny1998@gmail.com",
    description="Some Good Function In Django",
    install_requires=install_requires,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rezazeiny/django-autoutils",
    packages=packages,
    platforms=['linux'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
