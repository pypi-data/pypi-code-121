from distutils.core import setup

setup(name='browserlify',
      version='1.0.4',
      description='PDF generation, Web Scraping with headless chrome from browserlify.com',
      license='Apache Software License',
      author='browserlify',
      author_email='hello@browserlify.com',
      url='https://github.com/browserlify/python-sdk',
      packages=['browserlify'],
      requires=[
          "requests"
      ],
      scripts=['scripts/browserlify'],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Programming Language :: Python :: 3 :: Only',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: Apache Software License',
          'Topic :: Software Development :: Libraries',
          'Topic :: Scientific/Engineering :: Image Processing',
          'Topic :: Internet :: WWW/HTTP :: Browsers',
      ],
      )
