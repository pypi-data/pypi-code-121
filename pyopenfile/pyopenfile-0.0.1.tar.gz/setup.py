from setuptools import setup, find_packages

setup(
    name="pyopenfile",
    version="0.0.1",
    author="greene",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "uvicorn",
        "fastapi",
        "pydantic",
        "aiofiles",
        "python-dotenv",
        "requests",
        "click",
    ],
    entry_points={"console_scripts": ["openfile=app.__main__:main"]},
)
