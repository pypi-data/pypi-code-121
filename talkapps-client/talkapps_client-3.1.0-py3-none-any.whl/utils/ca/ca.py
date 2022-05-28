"""
Handles the certificate from Talk's CA
"""

from os.path import join, dirname

CACERT_PATH = join(dirname(__file__), 'cacert.pem')
