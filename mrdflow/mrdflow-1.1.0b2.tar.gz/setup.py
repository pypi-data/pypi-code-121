from setuptools import setup, find_packages

setup(
    name='mrdflow',
    version='1.1.0b2',
    description=(
        'This is a network.'
    ),
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    author='Zhou Chengyu',
    author_email='earuil@outlook.com',
    maintainer='Zhou Chengyu',
    maintainer_email='earuil@outlook.com',
    license='MIT License',
    packages = find_packages(),
    platforms=["all"],
    url='https://github.com/Zhou-chengy/mrdflow/',
    package_data={  # Optional
        'mrdflow': ['pytransform/_pytransform.dll'],
    },    
    install_requires=[
        "numpy",
    ]
    
)
