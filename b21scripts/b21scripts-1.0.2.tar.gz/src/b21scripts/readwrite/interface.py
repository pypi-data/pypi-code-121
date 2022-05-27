'''
Created on May 18, 2022

@author: nathan
'''

### A common interface contract for all readwrite classes
class Interface(object):    
    def parse_file(self): raise RuntimeError('Not implemented')
    def return_file(self): raise RuntimeError('Not implemented')
    def input_dict(self): raise RuntimeError('Not implemented')
    def return_dict(self): raise RuntimeError('Not implemented')
