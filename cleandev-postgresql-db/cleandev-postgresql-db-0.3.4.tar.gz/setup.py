import setuptools
import pathlib

HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()


setuptools.setup(
    name="cleandev-postgresql-db",
    version="0.3.4",
    author="Daniel Rodriguez Rodriguez",
    author_email="danielrodriguezrodriguez.pks@gmail.com",
    description="Module for handler postgresql more easy",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/cleansoftware/libs/public/cleandev-postgresql-db",
    project_urls={
        "Bug Tracker": "https://gitlab.com/cleansoftware/libs/public/cleandev-postgresql-db/-/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=[
        "postgresql_db",
    ],
    install_requires=[
        'psycopg2==2.9.1',
        'greenlet==1.1.2',
        'SQLAlchemy==1.4.27',
        'backports.strenum==1.1.1',
        'cleandev-config-loader==0.3.5',
        'cleandev-generic-utils==0.1.8'
    ],
    python_requires=">=3.9",
)
