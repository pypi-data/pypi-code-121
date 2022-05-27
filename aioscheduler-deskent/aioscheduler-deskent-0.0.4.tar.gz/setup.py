import setuptools

setuptools.setup(
    name="aioscheduler-deskent",
    version="0.0.4",
    author="Deskent",
    description="AIOScheduler",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7",
)
