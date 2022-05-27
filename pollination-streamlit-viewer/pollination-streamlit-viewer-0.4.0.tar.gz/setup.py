import setuptools

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="pollination-streamlit-viewer",
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    author="Pollination",
    author_email="nicolas@ladybug.tools",
    description="vtkjs component for streamlit",
    long_description="vtkjs component for streamlit",
    long_description_content_type="text/plain",
    url="https://github.com/pollination/pollination-streamlit-viewer",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.7",
    install_requires=requirements
)
