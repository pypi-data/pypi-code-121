from setuptools import setup

if __name__ == '__main__':
    with open('README.md', 'r') as file:
        long_description = file.read()

    setup(
        name='mvtec-halcon',
        version='22050.0.0',
        packages=['halcon'],
        package_data={'halcon': ['py.typed']},
        python_requires='>=3.8',

        author='MVTec Software GmbH',
        author_email='info@mvtec.com',
        description='Native Python language bindings for MVTec HALCON.',
        keywords='HALCON MVTec image processing',
        long_description=long_description,
        long_description_content_type='text/markdown',

        # Custom license support isn't ideal.
        license='Other/Proprietary License see eula.txt',
        data_files=[('', ['eula.txt'])],

        # Taken from here https://pypi.org/pypi?%3Aaction=list_classifiers
        # The classifiers field’s usefulness is openly disputed.
        # PyPI will refuse to accept packages with unknown classifiers.
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'Natural Language :: English',
            'License :: Other/Proprietary License',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: Implementation :: CPython',
            'Topic :: Scientific/Engineering :: Image Processing',
            'Topic :: Scientific/Engineering :: Visualization',
        ],
        url='https://www.mvtec.com/products/halcon',
    )
