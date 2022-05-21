from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="archetypewsgi",
    version="1.0.3",
    description="Python WSGI implementation for Archetype. Archetype provides packages that automatically handles API user auth and an SDK for managing your APIs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ArchetypeAPI/wsgi_sdk",
    author="Archetype Team",
    author_email="dev@archetype.dev",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=["requests", "Flask"],
    zip_safe=False,
)
