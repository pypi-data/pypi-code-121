from flask import Blueprint, jsonify, request

from ..status import Status


status_bp = Blueprint("/api/status", __name__, url_prefix="/api/status")


@status_bp.route("basic_status", methods=["GET"])
def return_basic_status():
    return jsonify(Status.utils.get_basic_status())


@status_bp.route("cpu_status", methods=["GET"])
def return_cpu_status():
    return jsonify(Status.utils.get_cpu_status(request.args.get("type")))


@status_bp.route("ram_status", methods=["GET"])
def return_ram_status():
    return jsonify(Status.utils.get_ram_status(request.args.get("type")))


@status_bp.route("disk_status", methods=["GET"])
def return_disk_status():
    return jsonify(Status.utils.get_disk_status(request.args.get("type")))


@status_bp.route("network_status", methods=["GET"])
def return_network_status():
    return jsonify(Status.utils.get_network_status(request.args.get("type")))

@status_bp.route("load_status", methods=["GET"])
def return_load_status():
    return jsonify(Status.utils.get_load_status(request.args.get("type")))

@status_bp.route("swap_status", methods=["GET"])
def return_swap_status():
    return jsonify(Status.utils.get_swap_status(request.args.get("type")))


@status_bp.route("interrupt_status", methods=["GET"])
def return_interrupt_status():
    return jsonify(Status.utils.get_interrupt_status(request.args.get("type")))

@status_bp.route("system_info", methods=["GET"])
def return_system_info():
    return jsonify(Status.utils.get_system_info())
