from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='fastapi_restful-extension',
    version='0.0.1',
    author="Shumilo Maxim",
    author_email="shumilo.mk@gmail.com",
    description='Extension for make RESTfull interfaces with FastAPI.',
    # Длинное описание, которое будет отображаться на странице PyPi. Использует README.md репозитория для заполнения.
    long_description="",
    install_requires=required,
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/maximshumilo/fastapi-restful-extension',
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # Требуемая версия Python.
    python_requires='>=3.6'
)
