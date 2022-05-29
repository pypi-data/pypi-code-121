import pyfirmata
from pyfirmata import Board, util, boards
import time
import asyncio
# from inspect import signature
import signal
import sys

def signal_handler(sig, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

CMD_LCD_DATA = 3
CMD_LCD_PRINT = 0
CMD_LCD_PUSH = 1
CMD_LCD_CLEAR = 2

CMD_MOTOR_DATA = 2
CMD_MOTOR_ON = 1
CMD_MOTOR_OFF = 2
CMD_MOTOR_INVERSE = 4
CMD_MOTOR_DIR = 5
CMD_MOTOR_SPEED = 6

SAMPLING_INTERVAL = 0x7A  # set the poll rate of the main loop
I2C_REQUEST = 0x76          # send an I2C read/write request
I2C_REPLY = 0x77            # a reply to an I2C read request
I2C_CONFIG = 0x78           # config I2C settings such as delay times and power pins
SET_DIGITAL_PIN = 0xF5         # set a pin value

HIGH = 0x01
LOW = 0x00
FIRMATA_7BIT_MASK = 0x7F

PIXEL_COMMAND =     0x51
PIXEL_OFF =         0x00
PIXEL_CONFIG =      0x01
PIXEL_SHOW =        0x02
PIXEL_SET_PIXEL =   0x03
PIXEL_SET_STRIP =   0x04
PIXEL_SHIFT =       0x05
SHIFT_FORWARD =     0x20
SHIFT_BACKWARD =    0x00

PING_READ =         0x75
SYSTEM_RESET =      0xFF


class __pyInterfaz(Board):

    def __init__(self, com_port, baudrate=115200, layout=None):
        super().__init__(com_port,  baudrate=baudrate, layout=layout)
        # IDENTIFICAMOS EL MODELO
        self.add_cmd_handler(pyfirmata.REPORT_FIRMWARE, self._handle_report_firmware)
        self.send_sysex(pyfirmata.QUERY_FIRMWARE, []);
        self.pass_time(0.1)  # Serial SYNC
        while self.bytes_available():
            self.iterate();
        self.load_board()
        # Necesitamos escribir directo sobre el puerto e indicamos conexión
        if self.led_builtin:
            self.sp.write([SET_DIGITAL_PIN,self.led_builtin,HIGH]);
            time.sleep(0.1)
            self.sp.write([SET_DIGITAL_PIN,self.led_builtin,LOW]);
        # Iniciamos loop para recibir datos
        it = util.Iterator(self)
        it.start()
        self.add_cmd_handler(I2C_REPLY, self._handle_i2c_message)
        self.add_cmd_handler(PING_READ, self._handle_ping_read)
        self.send_sysex(I2C_CONFIG, []);  # I2C_CONFIG
        self.lastMsg = ''

    def load_board(self):
        if self.firmware is not None:
            if hasattr(self, self.firmware):
                b = getattr(self, self.firmware)
                b()
                return
        # Si no podemos identificar por firmware lo hacemos por hardware
        m = None
        if len(self._layout['digital']) == 18 and len(self._layout['analog']) == 6: # Arduino UNO
            m = 'uno'
        elif len(self._layout['digital']) == 18 and len(self._layout['analog']) == 8: # Arduino Nano
            m = 'rasti'
        if m is not None and hasattr(self, m):
            b = getattr(self, m)
            b()
        else:
            raise ValueError("No se pudo identificar el modelo")

    def send_command(self, cmd):
        msg = bytearray([cmd])
        self.sp.write(msg)

    def reset(self):
        self.send_command(SYSTEM_RESET)

    def _handle_i2c_message(self, *args, **kwargs):
        address = util.from_two_bytes([args[0], args[1]])
        if address in self._i2c:
            x = self._i2c[address]
            if x.callBack is not None:
                values = []
                for i in range(2, len(args)-1, 2):
                    values.append(util.from_two_bytes([args[i], args[i+1]]))
                x.callBack(values)
                x.values[values[0]] = values[1:]


    def _handle_analog_message(self, pin_nr, lsb, msb):
        value = ((msb << 7) + lsb)
        # Only set the value if we are actually reporting
        try:
            if self.analog[pin_nr].reporting:
                ## CALL CALLBACK
                if self.analog[pin_nr].value != value:
                    for a in self._analogs:
                        if a.index == pin_nr:
                            a._changecb(value)
                self.analog[pin_nr].value = value
        except IndexError:
            raise ValueError

    def _handle_ping_read(self, pin_nr, *data):
        duration = (util.from_two_bytes(data[1:3]) << 24) \
                    + (util.from_two_bytes(data[3:5]) << 16) \
                    + (util.from_two_bytes(data[5:7]) << 8) \
                    + util.from_two_bytes(data[7:9])
        ping_distance = duration / 58.2
        # We can calculate the distance using an HC-SR04 as 'duration / 58.2'
        try:
            ## CALL CALLBACK
            if self.digital[pin_nr].ping_distance != ping_distance:
                for a in self._pings:
                    if a.index == pin_nr:
                        a._changecb(ping_distance)
            self.digital[pin_nr].ping_distance = ping_distance
        except IndexError:
            raise ValueError

    def _handle_report_capability_response(self, *data):
        charbuffer = []
        pin_spec_list = []

        for c in data:
            if c == pyfirmata.CAPABILITY_RESPONSE:
                continue

            charbuffer.append(c)
            if c == 0x7F:
                # A copy of charbuffer
                pin_spec_list.append(charbuffer[:])
                charbuffer = []

        self._layout = self.pin_list_to_board_dict(pin_spec_list)

    def pin_list_to_board_dict(self, pinlist):
        """
        Capability Response codes:
            INPUT:  0, 1
            OUTPUT: 1, 1
            ANALOG: 2, 10
            PWM:    3, 8
            SERV0:  4, 14
            I2C:    6, 1
            PULLUP: 11, 1
        """

        board_dict = {
            "digital": [],
            "analog": [],
            "pwm": [],
            "servo": [],  # 2.2 specs
            # 'i2c': [],  # 2.3 specs
            "disabled": [],
        }

        for i, pin in enumerate(pinlist):
            pin.pop()  # removes the 0x79 on end
            if not pin:
                board_dict["disabled"] += [i]
                #board_dict["digital"] += [i]
                continue

            capabilities = pin[::2]
            # Iterate over evens
            if 0 in capabilities and 1 in capabilities:
                board_dict["digital"] += [i]
            if 2 in capabilities:
                board_dict["analog"] += [i]
            if 3 in capabilities:
                board_dict["pwm"] += [i]
            if 4 in capabilities:
                board_dict["servo"] += [i]
            # Desable I2C
            if 6 in capabilities:
                pass

        # We have to deal with analog pins:
        # - (14, 15, 16, 17, 18, 19)
        # + (0, 1, 2, 3, 4, 5)
        diff = set(board_dict["digital"]) - set(board_dict["analog"])
        board_dict["analog"] = [n for n, _ in enumerate(board_dict["analog"])]

        # Digital pin problems:
        # - (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
        # + (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13)
        #board_dict["digital"] = [n for n, _ in enumerate(diff)]
        # Based on lib Arduino 0017
        #board_dict["servo"] = board_dict["digital"]
        board_dict["servo"] = [n for n, _ in enumerate(diff)]

        # Turn lists into tuples
        # Using dict for Python 2.6 compatibility
        board_dict = dict([(key, tuple(value)) for key, value in board_dict.items()])

        print(board_dict)
        return board_dict

    def output(self, index):
        if index < 0: index = 0
        return self._outputs[index]

    def input(self, index):
        if index < 0: index = 0
        return self._analogs[index]

    def digital_input(self, index):
        if index < 0: index = 0
        return self._digitals[index]

    def servo(self, index):
        if index < 0: index = 0
        return self._servos[index]

    def pin(self, index):
        if index < 0: index = 0
        return self._pins[index]

    def ping(self, index):
        if index < 0: index = 0
        return self._pings[index]

    def pixel(self, index):
        if index < 0: index = 0
        return self._pixels[index]

    def i2c(self, address):
        if not address in self._i2c: self._i2c[address] = self._I2C(self, address);
        return self._i2c[address]

    def joystick(self, index):  #index for compatibility
        return self._joystick;

    def lcd(self):
        return self._lcd

    def print(self, str1, str2):
        if not self._lcd is None:
            if not self.lcd()._silenciado:
                time.sleep(0.01)
                self.lcd().clear()
                self.lcd().print(0, str1)
                self.lcd().print(1, str2)
                time.sleep(0.01)
        self.lastMsg = ' '.join([str1, str2]);
        print(self.lastMsg)

    def loop(self):
        self.loop = asyncio.get_event_loop()
        self.loop.run_forever()

    def indexToDigitalPin(self, index):
        return index - 1 + 9

    class _LCD:

        def __init__(self, interfaz):
            self._interfaz = interfaz
            self._silenciado = False

        def _strtosysex(self, str):
            buf = []
            for char in str:
                buf.append(ord(char) & FIRMATA_7BIT_MASK)
                buf.append(ord(char) >> 7 & FIRMATA_7BIT_MASK)
            return buf

        def push(self, str):
            if self._silenciado:
                return  self;
            data = [CMD_LCD_PUSH]
            data += self._strtosysex(str)
            self._interfaz.send_sysex(CMD_LCD_DATA, data)
            return self

        def write(self, row, str):
            data = [CMD_LCD_PRINT, row]
            data += self._strtosysex(str)
            self._interfaz.send_sysex(CMD_LCD_DATA, data)
            return self

        def print(self, row, str):
            if self._silenciado:
                return  self;
            self.write(row,str);
            return self

        def clear(self):
            self._interfaz.send_sysex(CMD_LCD_DATA, [CMD_LCD_CLEAR])
            return self

        def silence(self):
            self._interfaz.print("LCD", "silenciado")
            self._silenciado = True
            return self

        def on(self):
            self._silenciado = False
            self._interfaz.print("LCD", "encendido")
            return self

    class _Servo:
        def __init__(self, interfaz, index):
            self._interfaz = interfaz
            self.index = index
            self.pin = self._interfaz.indexToDigitalPin(index)
            self._interfaz.servo_config(self.pin, angle=90)

        def position(self, pos):
            if pos < 0: pos = 0
            if pos > 180: pos = 180
            self._interfaz.digital[self.pin]._set_mode(pyfirmata.SERVO);
            self._interfaz.digital[self.pin].write(pos)
            self._interfaz.print("servo " + str(self.index), " posicion " + str(pos))

    class _Output:
        def __init__(self, interfaz, index):
            self._interfaz = interfaz
            self.index = index

        def on(self):
            self._interfaz.send_sysex(CMD_MOTOR_DATA, [CMD_MOTOR_ON, self.index])
            self._interfaz.print("salida " + str(self.index + 1), "encendido")
            return self

        def off(self):
            self._interfaz.send_sysex(CMD_MOTOR_DATA, [CMD_MOTOR_OFF, self.index])
            self._interfaz.print("salida " + str(self.index + 1), "apagado")
            return self

        def inverse(self):
            self._interfaz.send_sysex(CMD_MOTOR_DATA, [CMD_MOTOR_INVERSE, self.index])
            self._interfaz.print("salida " + str(self.index + 1), "invertido")
            return self

        def direction(self, d):
            if d > 0:
                d = 1
            else:
                d = 0
            self._interfaz.send_sysex(CMD_MOTOR_DATA, [CMD_MOTOR_DIR, self.index, d])
            self._interfaz.print("salida " + str(self.index + 1), "direccion " + str(d))
            return self

        def power(self, speed):
            if speed > 100: speed = 100
            if speed < 0: speed = 0
            self._interfaz.send_sysex(CMD_MOTOR_DATA, [CMD_MOTOR_SPEED, self.index, speed & FIRMATA_7BIT_MASK, speed >> 7 & FIRMATA_7BIT_MASK])
            self._interfaz.print("salida " + str(self.index + 1), "potencia " + str(speed))
            return self

    class _Joystick:
        def __init__(self, interfaz):
            self._interfaz = interfaz
            self.callBack = None
            self.address = 0x48

            self.i2c = self._interfaz.i2c(self.address)
            self.i2c.data(self.__callback)
            self._x = None
            self._y = None
            self._button = None

        def __callback(self, values):
            self.x = 1 if values[2] > 240 else -1 if values[2] < 50 else 0
            self.y = -1 if values[3] > 240 else 1 if values[3] < 50 else 0
            self.button = 1 if values[4] < 10 else 0
            if [self.x, self.y, self.button] != [self._x, self._y, self._button]:
                if self.callBack is not None:
                    self.callBack({"x": self.x, "y": self.y, "button": self.button})
            self._x = self.x
            self._y = self.y
            self._button = self.button

        def on(self, callback=None):
            operation = 4 | 0 | 0B01000000;
            self.i2c.write(operation).on(4)
            self._interfaz.print("Joystick" , "reportando")
            if callback is not None:
                self.data(callback)

        def data(self, callback):
            self.callBack = callback
            return self

        def off(self):
            self.data(None)
            self._interfaz.print("Joystick" , "detenido")

    class _I2C:
        def __init__(self, interfaz, address):
            self._interfaz = interfaz
            self.address = address & FIRMATA_7BIT_MASK
            self.callBack = None
            self.values = dict()

        def write(self, data):
            buf = [self.address, 0, data & FIRMATA_7BIT_MASK, data >> 7 & FIRMATA_7BIT_MASK]
            self._interfaz.send_sysex(I2C_REQUEST, buf)
            self._interfaz.print("I2C " + str(self.address), "escribiendo")
            return self

        def __doRead(self, buf, bytes, reg=None):
            if reg is not None:
                buf.append(reg & FIRMATA_7BIT_MASK)
                buf.append(reg >> 7 & FIRMATA_7BIT_MASK)
            buf.append(bytes & FIRMATA_7BIT_MASK)
            buf.append(bytes >> 7 & FIRMATA_7BIT_MASK)
            self._interfaz.send_sysex(I2C_REQUEST, buf)

        def read(self, bytes, reg=None, callback=None):
            buf = [self.address, 8]
            self.__doRead(buf, bytes, reg)
            if callback is not None:
                self.data(callback)
            self._interfaz.print("I2C " + str(self.address), "reportando")

        def on(self, bytes, reg=None, callback=None):
            buf = [self.address, 16]
            self.__doRead(buf, bytes, reg)
            if callback is not None:
                self.data(callback)
            self._interfaz.print("I2C " + str(self.address), "reportando")

        def off(self):
            self.data(None)
            self._interfaz.print("I2C" , "detenido")

        def data(self, callback):
            self.callBack = callback
            return self

    class __Sensor:
        def __init__(self):
            self.changeCallback = None
            pass

        def processCallback(self, callback):
            self.changeCallback = callback

        def _changecb(self, data):
            if not (self.changeCallback is None):
                self.changeCallback(data)
                """ 
                sig = signature(self.changeCallback)
                params = len(sig.parameters)
                if params == 1:
                    pass
                elif params == 2:
                    self.changeCallback(data, data)
                """

        def data(self, callback):
            self.processCallback(callback)
            return self

    class _PING(__Sensor):
        def __init__(self, interfaz, index):
            self._interfaz = interfaz
            self.index = index + 14
            self._interfaz.digital[self.index].ping_distance = -1;
            super().__init__()

        def ping(self):
            self.exec_ping();

        def exec_ping(self, trigger_mode=1, trigger_duration=10, echo_timeout=65000):
            """
            Trigger the pin and wait for a pulseIn echo.
            Used with HC-SR04 ultrasonic ranging sensors
            :arg trigger_mode: Uses value as a boolean,
                            0 to trigger LOW,
                            1 to trigger HIGH (default, for HC-SR04 modules).
            :arg trigger_duration: Duration (us) for the trigger signal.
            :arg echo_timeout: Time (us) to wait for the echo (pulseIn timeout).
            """
            if trigger_mode not in (0, 1):
                raise IOError("trigger_mode should be 0 or 1")

            # This is the protocol to ask for a pulseIn:
            #       START_SYSEX(0xF0)           // send_sysex(...)
            #       puseIn/pulseOut(0x74)       // send_sysex(PULSE_IN, ...)
            #       pin(0-127)
            #       value(1 or 0, HIGH or LOW)
            #       pulseOutDuration 0 (LSB)
            #       pulseOutDuration 0 (MSB)
            #       pulseOutDuration 1 (LSB)
            #       pulseOutDuration 1 (MSB)
            #       pulseOutDuration 2 (LSB)
            #       pulseOutDuration 2 (MSB)
            #       pulseOutDuration 3 (LSB)
            #       pulseOutDuration 3 (MSB)
            #       pulseInTimeout 0 (LSB)
            #       pulseInTimeout 0 (MSB)
            #       pulseInTimeout 1 (LSB)
            #       pulseInTimeout 1 (MSB)
            #       pulseInTimeout 2 (LSB)
            #       pulseInTimeout 2 (MSB)
            #       pulseInTimeout 3 (LSB)
            #       pulseInTimeout 3 (MSB)
            #       END_SYSEX(0xF7)             // send_sysex(...)

            data = bytearray()
            data.append(self.index)  # Pin number
            data.append(trigger_mode)  # Trigger mode (1 or 0, HIGH or LOW)
            trigger_duration_arr = util.to_two_bytes((trigger_duration >> 24) & 0xFF) \
                                   + util.to_two_bytes((trigger_duration >> 16) & 0xFF) \
                                   + util.to_two_bytes((trigger_duration >> 8) & 0xFF) \
                                   + util.to_two_bytes(trigger_duration & 0xFF)
            data.extend(trigger_duration_arr)  # pulseOutDuration
            echo_timeout_arr = util.to_two_bytes((echo_timeout >> 24) & 0xFF) \
                               + util.to_two_bytes((echo_timeout >> 16) & 0xFF) \
                               + util.to_two_bytes((echo_timeout >> 8) & 0xFF) \
                               + util.to_two_bytes(echo_timeout & 0xFF)
            data.extend(echo_timeout_arr)  # pulseInTimeout
            self._interfaz.send_sysex(PING_READ, data)


        def on(self, callback=None):
            self.processCallback(callback)
            self.ping()
            self._interfaz.print("ultrasonido " + str(self.index - 14), "reportando")


    class _Analog(__Sensor):
        def __init__(self, interfaz, index):
            self._interfaz = interfaz
            self.index = index
            super().__init__()

        def on(self, callback=None):
            self.processCallback(callback)
            self._interfaz.analog[self.index].enable_reporting()
            self._interfaz.print("sensor " + str(self.index + 1), "reportando")

        def report(self):
            self._interfaz.analog[self.index].enable_reporting()
            self._interfaz.print("sensor " + str(self.index + 1), "reportando")

        def read(self):
            return self._interfaz.analog[self.index].value

        def off(self):
            self._interfaz.analog[self.index].disable_reporting()
            self._interfaz.print("sensor " + str(self.index + 1), "apagado")

        def read(self):
            return self._interfaz.analog[self.index].value

        def set_sampling_interval(self, interval):
            self._interfaz.send_sysex(SAMPLING_INTERVAL, util.to_two_bytes(interval))

    class _Digital(__Sensor):
        def __init__(self, interfaz, index):
            self._interfaz = interfaz
            self.index = index
            self.pin  = index  + 14
            super().__init__()

        def on(self, callback=None):
            self.processCallback(callback)
            self._interfaz.digital[self.pin]._set_mode(pyfirmata.INPUT);
            self._interfaz.digital[self.pin].enable_reporting()
            self._interfaz.print("sensor dig. " + str(self.index + 1), "reportando")

        def off(self):
            self._interfaz.disable_digital_reporting(self.pin)
            self._interfaz.print("sensor dig. " + str(self.index + 1), "apagado")

        def read(self):
            return self._interfaz.digital_read(self.index)[0]

    class _Pin:
            def __init__(self, interfaz, index):
                self._interfaz = interfaz
                self.index = index
                self.pin = self._interfaz.indexToDigitalPin(index)

            def on(self):
                self._interfaz.digital[self.pin]._set_mode(pyfirmata.OUTPUT);
                self._interfaz.digital[self.pin].write(1)
                self._interfaz.print("digital " + str(self.index), " encendido ")

            def off(self):
                self._interfaz.digital[self.pin]._set_mode(pyfirmata.OUTPUT);
                self._interfaz.digital[self.pin].write(0)
                self._interfaz.print("digital " + str(self.index), " apagado ")

            def write(self, value):
                self._interfaz.digital[self.pin]._set_mode(pyfirmata.OUTPUT);
                self._interfaz.digital[self.pin].write(value)
                msg = " apagado " if value == 0 else " encendido "
                self._interfaz.print("digital " + str(self.index), msg)

    class _Pixel:
        def __init__(self, interfaz, index):
            self._interfaz = interfaz
            self.index = index
            self.pin = self._interfaz.indexToDigitalPin(index)
            self.length = 1

        def hex_to_rgb(self, hex):
            hex = hex.lstrip('#')
            hlen = len(hex)
            return tuple(int(hex[i:i + hlen // 3], 16) for i in range(0, hlen, hlen // 3))

        def hex_to_int(self, hex):
            colors = self.hex_to_rgb(hex)
            return (colors[0] << 16) + (colors[1] << 8) + (colors[2])

        def create(self, length):
            self.length = length
            self._interfaz.digital[self.pin]._set_mode(pyfirmata.OUTPUT);
            buf = [PIXEL_CONFIG, self.pin, self.length & FIRMATA_7BIT_MASK, self.length >> 7 & FIRMATA_7BIT_MASK]
            self._interfaz.send_sysex(PIXEL_COMMAND, buf)
            self._interfaz.print("pixel " + str(self.index), "configurado")
            return self

        def show(self):
            buf = [PIXEL_SHOW]
            self._interfaz.send_sysex(PIXEL_COMMAND, buf)
            return self

        def color(self, col, pos=0):
            # Color format in string hexa #RRGGBB
            if pos == 0:
                self.strip_color(col)
            else:
                color = self.hex_to_int(col)
                buf = [PIXEL_SET_PIXEL, pos & FIRMATA_7BIT_MASK, pos >> 7 & FIRMATA_7BIT_MASK, color & FIRMATA_7BIT_MASK, color >> 7 & FIRMATA_7BIT_MASK, color >> 14 & FIRMATA_7BIT_MASK, color >> 21 & FIRMATA_7BIT_MASK]
                self._interfaz.send_sysex(PIXEL_COMMAND, buf)
                self.show();
                self._interfaz.print("pixel " + str(self.index), col)
            return self

        def strip_color(self, col):
            # Color format in string hexa #RRGGBB
            color = self.hex_to_int(col)
            buf = [PIXEL_SET_STRIP, color & FIRMATA_7BIT_MASK, color >> 7 & FIRMATA_7BIT_MASK, color >> 14 & FIRMATA_7BIT_MASK, color >> 21 & FIRMATA_7BIT_MASK]
            self._interfaz.send_sysex(PIXEL_COMMAND, buf)
            self.show();
            self._interfaz.print("pixel " + str(self.index), col)
            return self

        def on(self, pos=0):
            color = "#FFFFFF"
            if pos > 0:
                self.color(color, pos)
            else:
                self.strip_color(color)
            self._interfaz.print("pixel " + str(self.index), "encendido")

        def off(self, pos=0):
            color = "#000000"
            if pos > 0:
                self.pixel_color(color, pos)
            else:
                self.strip_color(color)
            self._interfaz.print("pixel " + str(self.index), "apagado")

class interfaz(__pyInterfaz):
    def __init__(self, com_port):
        super().__init__(com_port, baudrate=115200, layout=None)

    def uno(self):
        self.modelo = "Uno";
        self.led_builtin = 13;
        self._lcd = self._LCD(self)
        self._outputs = [self._Output(self, 0), self._Output(self, 1), self._Output(self, 2), self._Output(self, 3)]
        self._servos = [self._Servo(self, 1), self._Servo(self, 2)]
        self._pins = [self._Pin(self, 1), self._Pin(self, 2)]
        self._pixels = [self._Pixel(self, 1), self._Pixel(self, 2)]
        self._analogs = [self._Analog(self, 0), self._Analog(self, 1), self._Analog(self, 2), self._Analog(self, 3)]
        self._digitals = [self._Digital(self, 0), self._Digital(self, 1), self._Digital(self, 2), self._Digital(self, 3)]
        self._pings = [self._PING(self, 0), self._PING(self, 1), self._PING(self, 2), self._PING(self, 3)]
        self._i2c = dict()
        self._joystick = self._Joystick(self)

    def rasti(self):
        self.led_builtin = 13;
        self.modelo = "Rasti";
        self._lcd = None
        self._outputs = [self._Output(self, 0), self._Output(self, 1)]
        self._servos = [self._Servo(self, 1), self._Servo(self, 2),self._Servo(self, 3), self._Servo(self, 4)]
        self._analogs = [self._Analog(self, 0), self._Analog(self, 1), self._Analog(self, 2), self._Analog(self, 3)]
        self._digitals = [self._Digital(self, 0), self._Digital(self, 1), self._Digital(self, 2), self._Digital(self, 3)]
        self._pings = [self._PING(self, 0), self._PING(self, 1), self._PING(self, 2), self._PING(self, 3)]
        self._i2c = dict()
        self._lcd = None
        self._joystick = self._Joystick(self)
        self._pins = [self._Pin(self, 1), self._Pin(self, 2)]
        self._pixels = [self._Pixel(self, 1), self._Pixel(self, 2)]

    def i32(self):
        self.led_builtin = 2;
        self._lcd = self._LCD(self)
        self._outputs = [self._Output(self, 0), self._Output(self, 1), self._Output(self, 2), self._Output(self, 3)]
        self._servos = [self._Servo(self, 1), self._Servo(self, 2)]
        self._analogs = [self._Analog(self, 0), self._Analog(self, 3), self._Analog(self, 6), self._Analog(self,7)]
        self._i2c = dict()
        self._joystick = self._Joystick(self)
        self._pins = [self._Pin(self, 1), self._Pin(self, 2)]
        self._pixels = [self._Pixel(self, 1), self._Pixel(self, 2)]


"""
def interfaz(com_port):
    boardlayout = {'digital': (),'analog': (),'pwm': (),'use_ports': False,'disabled': ()}
    b = Board(com_port, baudrate=115200, layout=None, timeout=2)
    modelo = b.firmware
    b.exit();
    # DEVOLVER LA INSTANCIA CORRESPONDIENTE AL FIRMWARE
    print(modelo)
    if modelo == "uno":
        return uno(com_port)
    elif modelo == "rasti":
        return rasti(com_port)
    raise Exception("Error en modelo de interfaz")
"""
