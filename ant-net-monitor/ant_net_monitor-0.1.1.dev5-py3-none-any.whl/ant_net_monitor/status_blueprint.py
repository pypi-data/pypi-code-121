from flask import Blueprint, jsonify, request
from ant_net_monitor.status.psutil_status.basic_status import BasicStatus

from ant_net_monitor.status.psutil_status.ram_status import RAMStatus

from .status.cpu_status import CPUStatus


status_bp = Blueprint("/api/status", __name__, url_prefix="/api/status")


@status_bp.route("basic_status", methods=["GET"])
def return_basic_status():
    return jsonify(BasicStatus.get_last())


@status_bp.route("cpu_status", methods=["GET"])
def return_cpu_status():
    if request.args.get("type") == "init":
        return jsonify(CPUStatus.get_batch())
    elif request.args.get("type") == "update":
        return jsonify(CPUStatus.get_last())
    elif request.args.get("type") == "day":
        return jsonify(CPUStatus.get_in_one_day())


@status_bp.route("ram_status", methods=["GET"])
def return_ram_status():
    if request.args.get("type") == "init":
        return jsonify(RAMStatus.get_batch())
    elif request.args.get("type") == "update":
        return jsonify(RAMStatus.get_last())
    elif request.args.get("type") == "day":
        return jsonify(RAMStatus.get_in_one_day())
