import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="freq_note_converter",
    version="0.2.0",
    author="Lior Israeli",
    author_email="israelilior@gmail.com",
    description="convert notes to freq and vise verse",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lisrael1/freq_note_converter",
    project_urls={
        "Bug Tracker": "https://github.com/lisrael1/freq_note_converter/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
          'dict_aligned_print',
      ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
