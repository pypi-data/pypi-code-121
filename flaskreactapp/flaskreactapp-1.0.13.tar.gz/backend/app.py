import os
from flask import Flask, send_from_directory

app = Flask(__name__, static_url_path='', static_folder='../frontend/build')

@app.route("/", defaults={'path':''})
def serve(path):
    return send_from_directory(app.static_folder,'index.html')


def import_by_reflection(name):
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

@app.route("/hello")
def hello():
    class_name = os.environ.get('suffix_class', 'backend.suffix.World')
    cls = import_by_reflection(class_name)
    obj = cls()
    return "Hello " + obj.get_suffix()

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)