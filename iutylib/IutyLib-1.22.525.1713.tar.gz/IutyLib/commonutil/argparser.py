from flask import reuest
import json

def getArgs(key=None,default=None):
    #form here
    if request.headers.get("Content-Type").startswith("application/x-www-form-urlencoded"):
        if key == None:
            return request.form
        else:
            arg = request.form.get(key)
            if arg == None:
                arg = default
            return arg
                
    #json here
    pass

class ArgPaser:
    def __init__(self):
        pass