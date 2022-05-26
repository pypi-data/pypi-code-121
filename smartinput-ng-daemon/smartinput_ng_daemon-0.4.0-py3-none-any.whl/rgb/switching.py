import multiprocessing
from smartinput.rgb.effects.rainbow import rainbow
from smartinput.rgb.effects.cycle import cycle
from smartinput.rgb.effects.breathe import breathe
from smartinput.rgb.effects.swap import swap
from smartinput.rgb.effects.static import static
from smartinput.rgb.helpers import RGBDevice
from smartinput.settings import settings_manager
import serial

effects = {
    "rainbow": {
        "function": rainbow,
        "friendly_name": "Rainbow",
        "options": {
            "speed": {
                "type": "int",
                "min": 1,
                "max": 100,
                "default": 20,
                "friendly_name": "Speed"
            }
        }
    },
    "cycle": {
        "function": cycle,
        "friendly_name": "Color Cycle",
        "options": {
            "speed": {
                "type": "int",
                "min": 1,
                "max": 100,
                "default": 20,
                "friendly_name": "Speed"
            }
        }
    },
    "breathe": {
        "function": breathe,
        "friendly_name": "Breathe",
        "options": {
            "speed": {
                "type": "int",
                "min": 1,
                "max": 100,
                "default": 20,
                "friendly_name": "Speed"
            },
            "num_colors": {
                "type": "int",
                "min": 2,
                "max": 20,
                "default": 6,
                "friendly_name": "Number of Colors"
            }
        }
    },
    "swap": {
        "function": swap,
        "friendly_name": "Swap",
        "options": {
            "speed": {
                "type": "int",
                "min": 1,
                "max": 100,
                "default": 20,
                "friendly_name": "Speed"
            },
            "color1": {
                "type": "color",
                "default": "#0000ff",
                "friendly_name": "Color 1"
            },
            "color2": {
                "type": "color",
                "default": "#ff0000",
                "friendly_name": "Color 2"
            }
        }
    },
    "static": {
        "function": static,
        "friendly_name": "Static",
        "options": {
            "color": {
                "type": "color",
                "default": "#ff0000",
                "friendly_name": "Color"
            }
        }
    },
}


class EffectSwitch:
    def __init__(self, device: serial.Serial):
        self.rgb_device = RGBDevice(serial_device=device)
        self.current_effect = None
        self.rgb_process = multiprocessing.Process(
            target=rainbow, args=(self.rgb_device,), daemon=True)

    def load_saved_effect(self):
        config = settings_manager.get_settings()
        if config.get("current_effect"):
            effect_name = config["current_effect"]
            options = config["effects"][effect_name]["options"]

            self.set_effect(effect_name, options)

    def set_effect(self, effect_name: str, options: dict):
        if effects.get(effect_name):
            effect = effects.get(effect_name)
            if self.rgb_process.is_alive():
                self.rgb_process.terminate()
            self.rgb_process = multiprocessing.Process(
                target=effect["function"], args=(self.rgb_device, options), daemon=True)
            config = settings_manager.get_settings()
            config["current_effect"] = effect_name

            if not config.get("effects"):
                config["effects"] = {}

            config["effects"][effect_name] = {"options": options}

            settings_manager.save_settings(config)
            self.rgb_process.start()
            self.current_effect = effect_name
        else:
            return ValueError("Effect not found")

    def get_effects_sanitized(self):
        sanitized = {}
        config = settings_manager.get_settings()
        for effect, data in effects.items():
            options_patched = data["options"]
            for option, option_data in options_patched.items():
                try:
                    option_data["current"] = config["effects"][effect]["options"][option]
                except KeyError:
                    option_data["current"] = option_data["default"]
                options_patched[option] = option_data

            sanitized[effect] = {
                "friendlyName": data["friendly_name"],
                "active": self.current_effect == effect,
                "options": options_patched
            }
        return sanitized
