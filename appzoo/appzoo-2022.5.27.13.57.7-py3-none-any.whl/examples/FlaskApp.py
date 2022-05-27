#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : FlaskApp
# @Time         : 2019-11-26 13:19
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 


from flask import Flask, request
from flask_restful import Api, Resource
from werkzeug.datastructures import ImmutableMultiDict

app = Flask(__name__)
api = Api(app)

class HelloWorld(Resource):
    def get(self):
        print(request.args)
        print(request.form)
        print(request.json)
        return 'get'

    def post(self):
        print(request.args)
        print(request.form)
        print(request.json)
        
        print(type(request.args))
        return 'post'


api.add_resource(HelloWorld, '/')

if __name__ == "__main__":
    app.run(debug=True)
