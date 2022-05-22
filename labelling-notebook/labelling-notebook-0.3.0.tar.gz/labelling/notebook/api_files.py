import json
import os
from typing import Dict

from flask import Blueprint, request, abort, jsonify, current_app, send_file

bp = Blueprint("files", __name__, url_prefix="/api/files")


@bp.route("")
def list_files():
    input_path = _resolve_input_key(request.args.get('path', ''))
    listing_path = input_path['path']

    if not os.path.isdir(listing_path):
        return abort(404, "Directory not found")

    output = []
    for path, subdirs, files in os.walk(listing_path):

        if path == listing_path:
            relative_path = ''
        else:
            relative_path = os.path.relpath(path, listing_path)
            if any([dirname.startswith('.') for dirname in relative_path.split('/')]):
                continue

            output.append({'key': relative_path + '/'})

        for filename in files:
            file_path = os.path.join(path, filename)
            if os.path.isdir(file_path):
                continue

            name, ext = os.path.splitext(filename)
            if ext in ('.jpg', '.png', '.jpeg'):
                file_mtime = os.path.getmtime(file_path)
                file_size = os.path.getsize(file_path)
                output.append({
                    'key': os.path.join(relative_path, filename),
                    'size': file_size,
                    'modified': file_mtime * 1000
                })
                continue

    return jsonify(output)


@bp.route("/image/<path:key>", methods=("GET",))
def get_image(key):
    image_path = _resolve_input_key(key)['path']

    if not os.path.isfile(image_path):
        return abort(404, "Image not found")

    return send_file(image_path)


@bp.route("/image_data/<path:key>", methods=("GET",))
def get_image_data(key):
    parsed_path = _resolve_input_key(key)
    image_path = parsed_path['path']
    data_path = parsed_path['path_without_ext'] + '.json'

    if not os.path.isfile(image_path):
        return abort(404, "Image not found")

    if not os.path.isfile(data_path):
        return abort(404, "Image data not found")

    with open(data_path, 'r') as f:
        return json.load(f)


@bp.route("/image_data/<path:key>", methods=("PUT", "POST",))
def put_image_data(key):
    parsed_path = _resolve_input_key(key)

    data = request.get_json(force=True)
    data_path = parsed_path['path_without_ext'] + '.json'

    with open(data_path, 'w') as f:
        json.dump(data, f)

    return data


def _resolve_input_key(input_key: str) -> Dict:
    path = os.path.join(current_app.instance_path, input_key)
    path_without_ext, ext = os.path.splitext(path)
    return {
        'path': path,
        'path_without_ext': path_without_ext,
        'ext': ext
    }
