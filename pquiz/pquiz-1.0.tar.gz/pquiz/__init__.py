"""
Ports quiz

A simple utility to check what ports are available for outgoing tcp
connection (ports 22 and 25 are not testable).

Gianluca Caronte 2019-2022 (c)

NOT RELATED TO http://portquiz.net, i just use it.
"""
__version__ = '1.0'
from .pquiz import test_port