from setuptools import find_packages
from setuptools import setup

setup(
    name="insight_gateway_python",
    author="htsc",
    version="4.0.28",
    author_email="insight@htsc.com",
    description="insight_gateway_python",
    long_description="insight_gateway_python",
    license='insightpythonsdk',
    project_urls={
        'Documentation': 'https://packaging.python.org/tutorials/distributing-packages/',
        'Funding': 'https://donate.pypi.org',
        'Source': 'https://github.com/pypa/sampleproject/',
        'Tracker': 'https://github.com/pypa/sampleproject/issues',
    },


    packages= ['insight_gateway_python_v400',
               'insight_gateway_python_v400/com',
               'insight_gateway_python_v400/com/interface',
               'insight_gateway_python_v400/com/libs/python37/x64',
               'insight_gateway_python_v400/com/cert'
               ],
    package_dir={'insight_gateway_python_v400/com/cert': 'insight_gateway_python_v400/com/cert',
                 'insight_gateway_python_v400/com/libs/python37/x64':
                     'insight_gateway_python_v400/com/libs/python37/x64'},
    package_data={'insight_gateway_python_v400/com/cert': ['HTInsightCA.crt', 'InsightClientCert.pem', 'HTISCA.crt', 'InsightClientKeyPkcs8.pem'],
                  'insight_gateway_python_v400/com/libs/python37/x64': ['_mdc_gateway_client.pyd', 'ACE.dll', 'ACE_SSL.dll', 'libeay32.dll', "ssleay32.dll"]},
    install_requires=[],

    python_requires='>=3.7.*',
)