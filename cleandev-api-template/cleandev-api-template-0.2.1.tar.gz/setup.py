import setuptools
import pathlib

HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setuptools.setup(
    name="cleandev-api-template",
    version="0.2.1",
    author="Daniel Rodriguez Rodriguez",
    author_email="danielrodriguezrodriguez.pks@gmail.com",
    description="Fachada para crear apis mas facilmente",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/cleansoftware/libs/public/cleandev-api-template",
    project_urls={
        "Bug Tracker": "https://gitlab.com/cleansoftware/libs/public/cleandev-api-template/-/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=[
        "api_template"
    ],
    install_requires=[
        "six==1.16.0",
        "click==8.0.3",
        "Flask==2.0.2",
        "PyJWT==2.3.0",
        "pytz==2021.3",
        "Jinja2==3.0.2",
        "Werkzeug==2.0.2",
        "aniso8601==9.0.1",
        "MarkupSafe==2.0.1",
        "Flask-Cors==3.0.10",
        "itsdangerous==2.0.1",
        "Flask-RESTful==0.3.9",
        "backports.strenum==1.1.1",
        "Flask-JWT-Extended==4.3.1",
        "cleandev-config-loader==0.3.5"
    ],
    python_requires=">=3.9",
)
