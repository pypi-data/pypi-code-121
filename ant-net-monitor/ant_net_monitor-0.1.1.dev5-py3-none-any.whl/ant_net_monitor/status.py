from flask import Blueprint, jsonify, request
from ant_net_monitor.status.psutil_status.basic_status import get_last_basic_status

from ant_net_monitor.status.psutil_status.ram_status import get_batch_ram_status, get_last_ram_status

from .Status.cpu_status import get_batch_cpu_status, get_last_cpu_status


status_bp = Blueprint("status", __name__, url_prefix="/status")


@status_bp.route("basic_status", methods=["GET"])
def return_basic_status():
    return jsonify(get_last_basic_status())


@status_bp.route("cpu_status", methods=["GET"])
def return_cpu_status():
    if request.args.get("type") == "init":
        return jsonify(get_batch_cpu_status())
    elif request.args.get("type") == "update":
        return jsonify(get_last_cpu_status())


@status_bp.route("ram_status", methods=["GET"])
def return_ram_status():
    if request.args.get("type") == "init":
        return jsonify(get_batch_ram_status())
    elif request.args.get("type") == "update":
        return jsonify(get_last_ram_status())
