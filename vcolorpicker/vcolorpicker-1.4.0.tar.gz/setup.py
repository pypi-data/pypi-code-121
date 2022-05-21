from setuptools import setup

setup(
    name='vcolorpicker',
    version='1.4.0',
    description='Open a visual vcolorpicker from any project.',
    url='https://github.com/nlfmt/pyqt-colorpicker',
    author='nlfmt',
    author_email='nlfmt@gmx.de',
    license='MIT',
    packages=['vcolorpicker'],
    install_requires=['pyqt5'],
    keywords=["python", "color", "gui", "colorpicker", "visual"],

    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)