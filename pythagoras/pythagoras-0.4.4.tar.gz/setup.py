import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="pythagoras"
    ,version="0.4.4"
    ,author="Volodymyr (Vlad) Pavlov"
    ,author_email="vlpavlov@ieee.org"
    ,description= "Simple and inexpensive way to create, deploy and run " 
        "cloud-scale algorithms from within local Python scripts and notebooks."
    ,long_description=long_description
    ,long_description_content_type="text/markdown"
    ,url="https://github.com/vladlpavlov/pythagoras"
    ,packages=["pythagoras"]
    ,classifiers=[
        "Development Status :: 3 - Alpha"
        , "Intended Audience :: Developers"
        , "Intended Audience :: Science/Research"
        , "Programming Language :: Python"
        , "Programming Language :: Python :: 3"
        , "License :: OSI Approved :: MIT License"
        , "Operating System :: OS Independent"
        , "Topic :: Scientific/Engineering"
        , "Topic :: Scientific/Engineering :: Information Analysis"
        , "Topic :: Software Development :: Libraries"
        , "Topic :: Software Development :: Libraries :: Python Modules"
    ]
    ,keywords='cloud, ML, AI, serverless, distributed, parallel'
              ', machine-learning, deep-learning, pythagoras'
    ,python_requires='>=3.9'
    ,install_requires=[
        'numpy'
        , 'scipy'
        , 'pandas'
        , 'scikit-learn'
        , 'jsonpickle'
        , 'psutil'
        , 'boto3'
        , 'moto'
        , 'pytest'
        , 'hypothesis'
    ]
    ,entry_points = {
        'console_scripts': [
            'pythagoras_oneoff_sharedstorage_worker = pythagoras:outprocess_one_off_worker'
        ]
    }

)