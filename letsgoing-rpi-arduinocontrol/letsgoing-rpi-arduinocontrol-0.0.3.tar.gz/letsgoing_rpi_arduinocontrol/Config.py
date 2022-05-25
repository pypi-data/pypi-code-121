#!/bin/python3
import json
import os
import shutil
from sys import argv
from getpass import getuser

from .Singleton import Singleton


class Pin:
    def __init__(self, internal, external):
        self.internal = internal # MCP23008
        self.external = external # Arduino

class Environment:
    def __init__(self, user, gpio, poti, cam):
        self.user = user
        self.gpio = gpio
        self.poti = poti
        self.cam = cam

class Config(Singleton):
    def __init__(self):
        install_path = os.path.dirname(os.path.realpath(__file__))
        self.resource_path = os.path.join(install_path,'resources')
        for i in range(2):
            config_path = os.path.expanduser('~/.config/letsgoing-rpi-arduinocontrol/')
            try:
                configFile = open(os.path.join(config_path, 'config.json'))
                config = json.load(configFile)
                break
            except:
                os.makedirs(config_path, exist_ok=True)
                src = os.path.join(self.resource_path, 'config.json')
                dst = os.path.join(config_path, 'config.json')
                shutil.copyfile(src, dst)

        self.pin_config_path = os.path.expanduser('~/.config/letsgoing-rpi-arduinocontrol/io-presets')
        for i in range(2):
            try:
                default_preset_file = open(os.path.join(self.pin_config_path, 'default'))
                default_preset_file.close()
                break
            except:
                os.makedirs(self.pin_config_path, exist_ok=True)
                src = os.path.join(self.resource_path, 'default_pinconfig.txt')
                dst = os.path.join(self.pin_config_path, 'default')
                shutil.copyfile(src, dst)

        self.environment = self.get_environment(config)
        
        
        
        self.pins = []
        for pin in config['pins']:
            self.pins.append(Pin(internal = pin['internal_GP'],
                                 external = pin['external_Pin']
                                ))

        self.buttons_per_row = config['general']['buttons_per_row']
        self.pollrate = config['general']['pollrate_ms']
        self.topmost = config['general']['topmost']

        self.video_allowed = config['video']['allowed']
        if (self.video_allowed):
            self.video_on_by_default = config['video']['on_by_default']
            self.video_warning = config['video']['enable_pop_up']
            if (self.video_warning):
                self.video_message_title = config['video']['pop_up_title']
                self.video_message = config['video']['pop_up_message']
            self.video_auto_off_ms = config['video']['auto_off_ms']
            self.videoResolution = (config['video']['resolution']['x'],
                                    config['video']['resolution']['y'])

        self.poti_highest = config['potiDisplay']['highest_value']
        self.poti_lowest = config['potiDisplay']['lowest_value']
        self.poti_resolution = config['potiDisplay']['resolution']
        self.poti_mouse_wheel_steps = config['potiDisplay']['mouse_wheel_steps']

        self.pin_modes = dict()
        for pin_mode in config['pinOptions']:
            self.pin_modes[pin_mode['name']] = pin_mode['function']

        configFile.close()

        self.about_content  = "Author: Tobias Glaser\n"
        self.about_content += "License: GNU GPLv2\n"
        self.about_content += "Issues and suggestions:\n"
        self.about_content += "https://github.com/tobiglaser/letsgoing-rpi-arduinocontrol\n"
        self.about_content += "\n"
        self.about_content += "At: Hochschule Reutlingen\n"
        self.about_content += "https://reutlingen-university.de\n"
        self.about_content += "\n"
        self.about_content += "For letsgoING\n"
        self.about_content += "https://letsgoing.org\n"

    def get_environment(self, config) -> Environment:
        user = self.determine_user()
        
        environment = -1
        for env in config['environments']:
            if env['username'] == user:
                environment = Environment(user = env['username'],
                                          gpio = env['gpio_address'],
                                          poti = env['poti_address'],
                                          cam  = env['camera']
                                         )
                pass

        if environment != -1:
            return environment
        else:
            raise Exception("Invalid User, check config.json")


    def determine_user(self) -> str:
        user = -1
        try:
            for i, arg in enumerate(argv):
                if arg == "-u":
                    user = (argv[i+1])
            if user == -1: 
                raise
        except:
            try:
                user = getuser()
            except:
                print("Could not determine User. Try passing \"-u USER\".")
        return user



config = Config()