from setuptools import setup, find_packages

setup(name='pyrebase_modific',
      version='1.2',
      description='Pyrebase modification with lists',
      author_email='lepeshokoff200@mail.ru',
      zip_safe=False,
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='Firebase',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'requests==2.27.1',
        'gcloud==0.17.0',
        'oauth2client==3.0.0',
        'requests_toolbelt==0.7.0',
        'python_jwt==2.0.1',
        'pycryptodome==3.4.3'
    ]
)