import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name="python-canvas",
    version="0.3.1",
    author="Nauryzbek Aitbayev",
    author_email="nauryzbek.aitbayev@yu.edu.kz",
    description="Данная библиотека содержить SqlAlchemy ORM для системы Canvas",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yessenovuniversity/python_canvas",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires = [
        'sqlalchemy',
        'psycopg2'
    ],
    python_requires='>=3.6',
)
