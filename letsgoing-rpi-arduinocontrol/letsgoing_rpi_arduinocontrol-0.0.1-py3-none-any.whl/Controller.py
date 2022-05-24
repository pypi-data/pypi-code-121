from .Singleton import Singleton
from .Config import config

from adafruit_mcp230xx.mcp23008 import MCP23008
import digitalio
import adafruit_ds3502
import board


class Controller(Singleton):
    def __init__(self):
        self.input_listeners = []
        
        self.i2c = board.I2C()

        self.ds3502 = adafruit_ds3502.DS3502(i2c_bus=self.i2c, address=config.environment.poti)
        self.oldPoti = -1
        self.set_poti(0)

        self.mcp = MCP23008(i2c=self.i2c, address=config.environment.gpio)
        self.pins = dict()
        for pin in config.pins:
            self.pins[pin.internal] = (self.mcp.get_pin(pin.internal))
        self.reset_IO()

    def poll_inputs(self) -> None:
        for listener in self.input_listeners:
            value = self.pins[listener.pin.internal].value
            listener.input_listener(value)
        pass

    def on_output_event(self, internal, state) -> None:
        self.pins[internal].value = state
        pass

    def register_input_listener(self, listener) -> None:
        self.input_listeners.append(listener)
        self.pins[listener.pin.internal].direction = digitalio.Direction.INPUT
        pass

    def unregister_input_listener(self, listener) -> None:
        while self.input_listeners.count(listener):
            self.input_listeners.remove(listener)
        self.pins[listener.pin.internal].direction = digitalio.Direction.OUTPUT
        pass

    def reset_IO(self) -> None:
        for pin in self.pins.values():
            pin.direction = digitalio.Direction.INPUT

    def set_poti(self, newValue) -> None:
        new_poti_val = int(127 * (float(newValue) / (config.poti_highest - config.poti_lowest)))
        self.ds3502.wiper = new_poti_val

    def on_exit(self) -> None:
        self.set_poti(0)
        self.reset_IO()

controll = Controller()