from setuptools import setup
setup(
    name="testingggggg",
    version="0.0.1",
    description="test",
    long_description = "This is a very very long description",
    author="dex",
    packages=['pack'],
    install_requires=[],
    extras_require={
        'extratesting': [
            'flask',
        ]
    }
)