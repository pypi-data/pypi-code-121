import setuptools

setuptools.setup(
    name="cleandev-framework",
    version="0.1.4",
    author="Daniel Rodriguez Rodriguez",
    author_email="danielrodriguezrodriguez.pks@gmail.com",
    description="Adaptadores de modelos de base de datos",
    url="https://gitlab.com/cleansoftware/libs/public/cleandev-framework",
    project_urls={
        "Bug Tracker": "https://gitlab.com/cleansoftware/libs/public/cleandev-framework/-/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=[
        "cleandev_framework"
    ],
    install_requires=[
        'cleandev-config-loader==0.3.5',
        'cleandev-generic-utils==0.1.8',
        'cleandev-validator==0.3.1',
        'cleandev-postgresql-db==0.3.4'
    ],
    python_requires=">=3.9",
)
