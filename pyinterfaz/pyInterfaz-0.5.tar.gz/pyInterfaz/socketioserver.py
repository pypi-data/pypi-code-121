from inspect import signature
from flask import Flask, render_template
from flask_socketio import SocketIO
import sys
import threading
import os

socket_port = 4268;

class SocketIOServer():
    def __init__(self, window):
        self.window = window
        # create a Socket.IO server
        if getattr(sys, 'frozen', False):
            template_folder = os.path.join(sys._MEIPASS, 'templates')
        else:
            template_folder = os.path.join(os.getcwd(), "templates")
        sioapp = Flask(__name__, template_folder=template_folder)
        sioapp.config['SECRET_KEY'] = 'robotica.ar'
        sio = SocketIO(sioapp, async_mode='threading', cors_allowed_origins='*')
        self.sio = sio
        self.sioapp = sioapp
        x = threading.Thread(target=self.start_server, args=(), daemon=True)
        x.start()
        self.log("Servidor socket corriendo en: http://127.0.0.1:"+str(socket_port))

        @sioapp.route('/')
        def index():
            return render_template('index.html')

        @sioapp.route('/socket.io.min.js')
        def socket_io():
            return render_template('socket.io.min.js')

        @sio.on('SYSTEM_RESET')
        def reset_message():
            if hasattr(self.window, "i"):
                self.window.i.reset()

        @sio.on('OUTPUT')
        def output_message(b):
            self.exec("output", b)

        @sio.on('ANALOG')
        def analog_message(b):
            if b['method'] == "read":
                value = self.exec("input", b)
                print(value)
                if value is not None:
                    self.emit_report("ANALOG_MESSAGE", b['index'], value)
            else:
                self.exec("input", b, lambda d: self.emit_report("ANALOG_MESSAGE", b['index'], d))

        @sio.on('DIGITAL')
        def digital_message(b):
            self.exec("digital_input", b, lambda d: self.emit_report("DIGITAL_MESSAGE", b['index'], d))

        @sio.on('SERVO')
        def servo_message(b):
            self.exec("servo", b)

        @sio.on('LCD')
        def lcd_message(b):
            self.exec("lcd", b)

        @sio.on('PIXEL')
        def pixel_message(b):
            self.exec("pixel", b)

        @sio.on('PIN')
        def servo_message(b):
            self.exec("pin", b)

        @sio.on('PING')
        def ping_message(b):
            self.exec("ping", b, lambda d: self.emit_report("PING_MESSAGE", b['index'], d))

        @sio.on('I2CJOYSTICK')
        def i2cjoystick_message(b):
            self.exec("joystick", b, lambda d: self.emit_report("I2CJOYSTICK_MESSAGE", b['index'], d))

        @sio.on('I2C')
        def i2c_message(b):
            if b['method'] in ["on","read"]:
                self.exec("i2c", b, lambda d: self.emit_report("I2C_MESSAGE", b['address'], d))
            else:
                self.exec("i2c", b)

    def start_server(self):
        self.sio.run(self.sioapp, port=socket_port)

    def emit_report(self, key, index, data):
        self.sio.start_background_task(target=self.emit(key, {'index': index, 'value': data}))

    def emit(self, key, value):
        self.sio.emit(key, value)

    def exec(self, obj, data, callback=False):
        print('Received data: ', data)
        if not self.pre(): return
        o = getattr(self.window.i, obj)
        if 'address' in data:
            data['index'] = data['address']
        if 'index' in data:
            f = getattr(o(data['index']), data['method'])
        else:
            f = getattr(o(), data['method'])
        sig = signature(f)
        params = list(sig.parameters.values())
        result = None
        try:
            if len(sig.parameters) == 0:
                result = f()
            elif len(sig.parameters) == 1:
                if callback:
                    result = f(callback)
                else:
                    # checkear si vienen los parametros opcionales
                    if not ('param' in data) and not (params[0].default is params[0].empty):
                        data['param'] = params[0].default
                    result = f(data['param'])
            elif len(sig.parameters) == 2:
                if obj == "i2c":
                    if not 'param' in data:
                        data['param'] = None
                    result = f(data['param'], data['register'])
                else:
                    # checkear si vienen los parametros opcionales
                    if not ('param2' in data) and not (params[1].default is params[1].empty):
                        data['param2'] = params[1].default
                    result = f(data['param'], data['param2'])
            elif len(sig.parameters) == 3:
                if obj == "i2c":
                    if not 'param' in data:
                        data['param'] = None
                    if not callback:
                        callback = None
                    result = f(data['param'], data['register'], callback)
                else:
                    # checkear si vienen los parametros opcionales
                    if not ('param2' in data) and not (params[1].default is params[1].empty):
                        data['param2'] = params[1].default
                    if not ('param3' in data) and not (params[2].default is params[2].empty):
                        data['param3'] = params[2].default
                    result = f(data['param'], data['param2'], data['param3'])
            self.log(self.window.i.lastMsg)
            return result
        except Exception as inst:
            self.log("No se ha podido ejecutar el comando: "+obj)
            print(inst)

    def log(self, msg):
        self.window.consoleTrigger.emit(msg)

    def pre(self):
        if not hasattr(self.window, "i"):
            self.log("No hay interfaz conectada")
            return False
        if not self.window.i:
            self.log("No hay interfaz conectada")
            return False
        return True