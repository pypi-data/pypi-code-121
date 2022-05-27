import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = []
with open("requirements.txt", "r") as requirements_file:
    requirements.append(requirements_file.read())

    # How mature is this project? Common values are
    #   1 - Planning
    #   2 - Development
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    # 'License :: OSI Approved :: MIT License',
    # 'Development Status :: 3 - Alpha',
    # "Intended Audience :: Developers",
    # "Topic :: Communications",
    # "Topic :: Utilities"
    # "Programming Language :: Python",
classifiers = [
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
]

setuptools.setup(
    name="SmartSignals",
    version="0.0.0",
    author="Uwe Roder",
    author_email="uweroder@gmail.com",
    description="The SmartSignal lib is an event driven system similar to QT.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/grobbles/SmartSignals",
    packages=["smart_signals"],
    license='MIT',
    # classifiers=classifiers,
    python_requires='>=3.7',
    keywords=["smart_signals", "SmartSignals", "signals", "events", "slot", "qt"],
    install_requires=requirements
)
