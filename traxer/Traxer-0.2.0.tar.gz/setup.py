from setuptools import find_packages, setup
import os 

# Source : MLflow repository https://github.com/mlflow/mlflow/blob/master/setup.py
# Get a list of all files in the JS directory to include in our module
def package_files(directory):
    paths = []
    for (path, _, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join("..", path, filename))
    return paths

template_files = package_files("traxer/server/frontend/build") + ["traxer/client/api_calls.yaml"]
static_files = package_files("traxer/server/frontend/public")

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name="Traxer",
    long_description=long_description,
    long_description_content_type='text/x-rst',
    packages=find_packages(),
    version = "0.2.0",
    description="Track and visualize your experiments",
    author="Jules Tevissen",
    license="MIT",
    install_requires=[
        "numpy", 
        "bokeh", 
        "mongoengine", 
        "Flask", 
        "flask-cors", 
        "pyyaml", 
        "click", 
        "gunicorn",
        "psutil"
    ],
    package_data={"traxer": template_files + static_files}, 
    entry_points={
        "console_scripts": [
            "traxer=traxer.server.run_server:run"
        ]
    },
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)