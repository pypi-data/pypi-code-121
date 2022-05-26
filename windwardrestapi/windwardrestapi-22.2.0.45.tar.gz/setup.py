import setuptools
import distutils.sysconfig

from setuptools import Distribution


class BinaryDistribution(Distribution):
    def has_ext_modules(foo):
        return True

setuptools.setup(
    name= 'windwardrestapi',
	version= "22.2.0.45",
    description = 'Python client for the Windward RESTful Engine',
    long_description = '',
    url = 'http://www.windward.net/products/restful/',
    author = 'Windward Studios',
    author_email ='support@windward.net',
    install_requires = ['requests', 'six'],
    package_dir={'': 'dist-obfu'},
    packages = setuptools.find_packages(where='dist-obfu'),
    # data_files = [(distutils.sysconfig.get_python_lib(), ["dist-obfu/windwardrestapi/pytransform/_pytransform.dll"])],
    data_files = [("pytransform", ["dist-obfu/windwardrestapi/pytransform/_pytransform.so"])],
    package_data = {"" : ['dist-obfu/windwardrestapi/pytransform/_pytransform.so']},
    include_package_data = True,
    include_data_files = True,
    distclass=BinaryDistribution

)
