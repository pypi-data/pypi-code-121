from __future__ import absolute_import
from distutils.core import setup


setup(name='superops-talon',
	packages = ['talon'],
      version='0.1',
      description=("Mailgun library "
                   "to extract message quotations and signatures (talon-1.6.0)"),
      author='SuperOps.ai',
      author_email='app.integrations@superops.ai',
      license='APACHE2',
      
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          "lxml",
          "regex",
          "numpy",
          "scipy",
          "scikit-learn>=1.0.0",
          "chardet",
          "cchardet",
          "cssselect",
          "six",
          "html5lib",
          "joblib",
          ],
      tests_require=[
          "mock",
          "nose",
          "coverage"
          ]
      )
