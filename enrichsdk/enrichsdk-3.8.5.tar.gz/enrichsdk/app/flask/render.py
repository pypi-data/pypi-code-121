import os
import json
import traceback

from flask import Flask, render_template, request
from flask_multistatic import MultiStaticFlask

app = MultiStaticFlask(__name__)


@app.route("/")
def main():

    print(request.args)
    # First get the arguments if any
    params = {}
    for name in request.args:
        valuelist = request.args.getlist(name)
        params[name] = valuelist

    try:
        skin = app.config["skin"]
        data = skin.render(params)
    except:
        traceback.print_exc()
        data = [
            {
                "target": "result",
                "rendered": "<p class='lead'>Error while rendering</p>",
            }
        ]

    return render_template("index.html", data=data)


def shutdown_server():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()


@app.route("/shutdown")
def shutdown():
    shutdown_server()
    return "Server shutting down..."


# Custom static data
@app.route("/app/static/<path:filename>")
def custom_static(filename):
    for p in app.config["static_paths"]:
        fullpath = os.path.join(p, filename)
        if os.path.exists(fullpath):
            return send_from_directory(p, filename)


def create_app(conf):

    # => Set the static folder...
    static_paths = conf.pop("static_paths")
    static_paths.insert(0, os.path.join(app.root_path, "static"))
    app.static_folder = static_paths

    app.config.update(conf)
    return app


if __name__ == "__main__":
    app.run(debug=True)
