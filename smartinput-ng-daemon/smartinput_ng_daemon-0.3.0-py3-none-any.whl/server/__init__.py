from crypt import methods
import multiprocessing
import threading
from typing import Optional
import serial
from flask import Flask, request, jsonify
from smartinput.rgb.effects.rainbow import rainbow
from smartinput.rgb.helpers import RGBDevice
from smartinput.rgb.switching import effects, EffectSwitch

app = Flask(__name__)
rgb_switch: Optional[EffectSwitch] = None


@app.route("/set_effect/<effect_name>", methods=["POST"])
def set_effect(effect_name):
    if effects.get(effect_name):
        print(request.json)
        rgb_switch.set_effect(effect_name, request.json or {})
        return jsonify({"status": "OK"})
    else:
        return jsonify({"error": "Effect not found"}), 404


@app.route("/effects")
def get_effects():
    return jsonify(rgb_switch.get_effects_sanitized())


def run_in_thread(device: serial.Serial, host="127.0.0.1", port=12853):
    global rgb_switch
    rgb_switch = EffectSwitch(device)
    rgb_switch.load_saved_effect()
    thread = threading.Thread(target=lambda: app.run(
        host=host, port=port, debug=False, use_reloader=False))
    thread.start()
    return thread
