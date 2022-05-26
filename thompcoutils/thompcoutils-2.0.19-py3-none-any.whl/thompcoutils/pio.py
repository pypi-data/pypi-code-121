import datetime
from thompcoutils.log_utils import get_logger
import threading
import sys
import thompcoutils.units as units
from queue import Queue
from enum import Enum
import time
from thompcoutils.pio_exception import PioException
from thompcoutils.threading_utils import WorkerLoopThread, WorkerThread

# noinspection PyBroadException
try:
    import RPi.GPIO as GPIO
    import Adafruit_ADS1x15
    import Adafruit_DHT
    import smbus

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    pio_loaded = True
    get_logger().debug('GPIO successfully loaded')
except Exception as e:
    pio_loaded = False
    raise PioException('GPIO not loaded because {}'.format(e))


class ADC:
    class SensorType(Enum):
        ADS1115 = 0
        ADS1015 = 1

    class Values:
        def __init__(self, values, voltages):
            """
            Values are retrieved by the _get_data_thread and loaded into a Values object that is then pushed onto the
            queue.
            :param values: array of values from the ADC
            :param voltages: array of voltages from the ADC
            """
            self.time_stamp = datetime.datetime.now()
            self.values = values
            self.voltages = voltages

    @staticmethod
    def _get_data_thread(adc):
        logger = get_logger()
        """
        _get_data_thread retrieves the data values from the adc and pushes them onto the thread.  It is called via a
        thread and runs in a loop until stopped.
        :param adc: the ADC (should be self)
        :return: None
        """
        values = [0] * 4
        voltages = [0] * 4
        for i in range(4):
            values[i] = adc.adc.read_adc(i, gain=adc.gain)
            v2 = values[i] * adc.multiplier
            v3 = ((adc.r1 * v2) / adc.r2) + v2
            voltages[i] = v3
            if v3 > adc.last_voltage[i] + adc.tolerance or v3 < adc.last_voltage[i] - adc.tolerance:
                append = True
            adc.last_voltage[i] = v3
        # print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} |'.format(*values))
        logger.debug('| {0:.2f} | {1:.2f} | {2:.2f} | {3:.2f} |'.format(*voltages))
        adc.queue.put_nowait(adc.Values(values, voltages))
        time.sleep(adc.update)

    def __init__(self, chip_type=SensorType.ADS1115, gain=1, r1=1000000, r2=220000, tolerance=.1, update=.25):
        """
        An Analog to Digital Converter (ADC) converts analog values to digital ones.
        :param chip_type: the type of the chip (from ADC.SensorType)
        :param gain: gain required to amplify the signal
        :param r1: R1 from a resistor voltage splitter
        :param r2: R2 from a resistor voltage splitter
        :param tolerance: amount of tolerance allowed
        :param update: amount of time to sleep between  adc readings
        """
        self.gains = {1: 4.096, 2: 6.144, 3: 6.144, 4: 1.024, 8: 0.512, 16: 0.256}
        self.gain = gain
        self.r1 = r1
        self.r2 = r2
        self.tolerance = tolerance
        self.update = update
        self.queue = Queue(1000)
        self.last_voltage = [0] * 4
        self.worker_thread = None

        # Create an ADS1115 ADC (16-bit) instance.
        if chip_type == ADC.SensorType.ADS1115:
            self.adc = Adafruit_ADS1x15.ADS1115()
            self.resolution_range = {min: -32768, max: 32767}
        elif chip_type == ADC.SensorType.ADS1015:
            self.adc = Adafruit_ADS1x15.ADS1015(address=0x49, busnum=1)
            self.resolution_range = {min: -2048, max: 2047}
        else:
            raise RuntimeError("Invalid Chip Type:{}".format(chip_type))
        self.multiplier = 2 * self.gains[gain] / (self.resolution_range[max] - self.resolution_range[min])

    def start(self):
        """
        Starts the ADC._get_data_thread loop
        """
        if self.worker_thread and self.worker_thread.is_running():
            return

        # empty the queue
        while not self.queue.empty():
            self.queue.get_nowait()
        self.worker_thread = WorkerLoopThread(callback_function=ADC._get_data_thread, parameters=self)
        self.worker_thread.start()

    def stop(self):
        """
        Stops the ADC._get_data_thread loop
        """
        if self.worker_thread and self.worker_thread.is_running():
            self.worker_thread.stop()
            self.worker_thread = None

    # noinspection PyProtectedMember
    def is_running(self):
        """
        Indicates the ADC._get_data_thread is running
        :return: True or False if running/not running
        """
        return self.worker_thread and self.worker_thread.is_running()


class Button:
    def __init__(self, pin, callback=None, pull_up_down=GPIO.PUD_UP, package=None):
        """
        Represents a button on the pi.
        check out this article on debouncing:
        https://www.raspberrypi.org/forums/viewtopic.php?t=134394
        :param pin: pin the button is on
        :param callback: callback to call when pressed
        :param pull_up_down: defines if the button is pulled up or down with a resistor
        :param package: package to be passed to the callback function (generally self)
        """
        self.pin = pin
        self.package = package
        self.last_push = datetime.datetime.now()
        self.callback = callback
        GPIO.setup(pin, GPIO.IN, pull_up_down=pull_up_down)
        GPIO.add_event_detect(pin, edge=GPIO.BOTH, callback=self._debounce_function)
        self.current_state = None

    def _debounce_function(self, pin):
        """
        This function debounces the button.  Buttons are inherently noisy (they ring when pressed)  This function waits
        a period of time before declaring the button to have settled into the current state.
        :param pin: pin the button is on
        :return: None
        """
        time_now = datetime.datetime.now()
        current_state = GPIO.input(self.pin)
        if (time_now - self.last_push).microseconds > .1 * units.microseconds_per_second:
            self.current_state = current_state
            if self.callback is not None:
                self.callback(pin, current_state, self.package)
        self.last_push = time_now


class TimedButton:
    def __init__(self, pin, callback, pull_up_down=GPIO.PUD_UP, package=None):
        """
        A TimedButton initiates a callback after a button has been pressed and then released.  It passes the duration
        the button was pressed to the callback
        :param pin: pin the button is on
        :param callback: callback to call when pressed
        :param pull_up_down: indicates the button is pulled up or down with a resistor
        :param package: package to pass to the callback
        """
        self.pin = pin
        self.package = package
        self.last_push = datetime.datetime.now()
        self.callback = callback
        self.press_time = None
        GPIO.setup(pin, GPIO.IN, pull_up_down=pull_up_down)
        GPIO.add_event_detect(pin, edge=GPIO.BOTH, callback=self._debounce_function)

    def _debounce_function(self, pin):
        """
        This function debounces the button.  Buttons are inherently noisy (they ring when pressed)  This function waits
        a period of time before declaring the button to have settled into the current state.
        :param pin: pin the button is on
        :return: None
        """
        time_now = datetime.datetime.now()
        current_state = GPIO.input(self.pin)
        if (time_now - self.last_push).microseconds > .1 * units.microseconds_per_second:
            if current_state and self.press_time is not None:
                self.callback(pin, datetime.datetime.now() - self.press_time, self.package)
            else:
                self.press_time = datetime.datetime.now()
        self.last_push = time_now


class LightSensor:
    """
    Defines a Light Sensor that is built from an RC circuit.  It takes a certain amount of time for the capacitor to
     charge.
     If it charges to above the threshold in the charge_time, the light detector says it is on.
     If it fails to charge in the charge_time, it is said to be off
    """

    def __init__(self, pin_number, charge_time, discharge_time):
        """
        Constructs a LightSensor

        :param pin_number: the pin the circuit is attached to
        :param charge_time: the minimum time required to charge the capacitor for the circuit to be considered on
        :param discharge_time: the time required to discharge the capacitor for the circuit to be considered off
        """
        self.pin_number = pin_number
        self.charge_time = charge_time
        self.discharge_time = discharge_time
        self.current_state = 0

    def discharge(self):
        """
        Discharges the capacitor by writing a 0 to the pin then waiting the discharge time
        """
        GPIO.setup(self.pin_number, GPIO.OUT)
        GPIO.output(self.pin_number, GPIO.LOW)

    def read_value(self):
        """
        Reads the value by flipping the pin back to an input and waiting the charge time
        :return: the current state of the LightSensor
        """
        GPIO.setup(self.pin_number, GPIO.IN)
        current_time = time.time()
        diff = 0
        read_value = GPIO.LOW

        # keep reading the input until the value turns on or times out
        while read_value == GPIO.LOW and diff < self.charge_time:
            read_value = GPIO.input(self.pin_number)
            diff = time.time() - current_time

        if GPIO.input(self.pin_number) == GPIO.LOW:
            self.current_state = 0
        else:
            self.current_state = 1

        return self.current_state

    def check_for_light(self):
        """
        Checks for light. This resets the pin, grounding the capacitor, then sets back to input and waits the charge_time
        for the capacitor to charge.  It calls self.discharge() then self.read_value()

        :return: True if the capacitor charges within the minimum time, False if not
        """
        # discharge the capacitor
        self.discharge()
        # start reading the input pin
        time.sleep(self.discharge_time)
        return self.read_value()


class PiOut:
    def __init__(self, pin, initial_state=None):
        """
        Defines an  output pin for the pi
        :param pin: Pin to control
        :param initial_state: True (up) or False (down)
        """
        if pio_loaded:
            GPIO.setup(pin, GPIO.OUT)
        self.pin = pin
        self.state = False
        if initial_state is not None:
            self.toggle(initial_state)

    def toggle(self, new_state=None):
        """
        Toggles the current state of new_state is not provided
        :param new_state: state to force the pin to
        :return: None
        """
        logger = get_logger()
        if new_state is None:
            self.state = not self.state
        else:
            self.state = new_state
        logger.debug("pin {} toggled {}".format(self.pin, self.state))
        if pio_loaded:
            GPIO.output(self.pin, self.state)

    def turn_on(self):
        """
        Turns on the output to this PiOut's pin
        :return: None
        """
        if not self.state:
            self.state = True
            GPIO.output(self.pin, True)

    def turn_off(self):
        """
        Turns off the output to this PiOut's pin
        :return: None
        """
        if self.state:
            self.state = False
            GPIO.output(self.pin, False)

    def is_on(self):
        """
        Indicates whether the pin is high or low
        :return: True if high, False if low
        """
        return self.state


class Led(PiOut):
    def __init__(self, pin, initial_state=None):
        """
        Basic LED.
        :param pin: Pin the LED is on
        :param initial_state: True for on, False for off
        """
        PiOut.__init__(self, pin, initial_state)


class Relay(PiOut):
    def __init__(self, pin, initial_state=None):
        """
        Relay is a very basic PIO device
        :param pin: Pin the relay is on
        :param initial_state: True for on, False for off
        """
        PiOut.__init__(self, pin, initial_state)


class FlashingLed(Led):
    def __init__(self, pin, on_off, count=None, initial_state=None):
        """
    Flashing LED is an LED that flashes
        :param pin: Pin the relay is on
        :param on_off: time (milliseconds) the led is [on, off]
        :param count: Number of times to flash (None is forever)
        :param initial_state:
        """
        PiOut.__init__(self, pin, initial_state)
        self.on_off = on_off
        self.count = count
        self.worker_thread = None

    # noinspection PyProtectedMember
    def _flasher(self):
        """
        This is the callback that flashes the LED on and off.  It is called once by start()
        :return: None
        """
        logger = get_logger()
        self.toggle(True)
        logger.debug("FlashingLight pin {} is {}".format(self.pin, self.state))
        time.sleep(self.on_off[0])
        if self.worker_thread._is_running:
            self.toggle(False)
        logger.debug("FlashingLight pin {} is {}".format(self.pin, self.state))
        time.sleep(self.on_off[1])

    def start(self):
        """
        This method starts the LED flashing.
        :return: None
        """
        if self.worker_thread is None:
            self.worker_thread = WorkerThread(callback_function=self._flasher)
            self.worker_thread.start()

    def stop(self):
        """
        This method stops the LED from flashing
        :return: None
        """
        if self.worker_thread is not None:
            self.worker_thread.stop_flashing()
            self.worker_thread = None


class ColorLed:
    def __init__(self, red_pin, green_pin, blue_pin):
        """
        ColorLed is a color led that can be flashed.
        :param red_pin: pin number for red
        :param green_pin: pin number for green
        :param blue_pin: pin number for blue
        """
        self._red = Led(red_pin)
        self._green = Led(green_pin)
        self._blue = Led(blue_pin)
        self.turn_off()
        self.on_off = []
        self.colors = []
        self._flasher_running = False
        self._flashing = False

    def set_colors(self, colors):
        """
        Sets the colors for the led
        :param colors: array of boolean [red, green, blue]
        :return: None
        """
        self.colors = colors

    def turn_on(self):
        """
        Turns on the colors with the colors set in set_colors()
        :return: None
        """
        self._red.toggle(self.colors[0])
        self._green.toggle(self.colors[1])
        self._blue.toggle(self.colors[2])

    def red(self):
        """
        Turns the led red
        :return: None
        """
        self.set_colors([False, True, True])
        self.turn_on()

    def green(self):
        """
        Turns the led green
        :return: None
        """
        self.set_colors([True, False, True])
        self.turn_on()

    def blue(self):
        """
        turns the led blue
        :return: None
        """
        self.set_colors([True, True, False])
        self.turn_on()

    def yellow(self):
        """
        turns the led yellow using red & green
        :return: None
        """
        self.set_colors([False, False, True])
        self.turn_on()

    def magenta(self):
        """
        turns the led magenta using red & blue
        :return: None
        """
        self.set_colors([False, True, False])
        self.turn_on()

    def cyan(self):
        """
        turns the led cyan using blue & green
        :return: None
        """
        self.set_colors([True, False, False])
        self.turn_on()

    def white(self):
        """
        turns the led white using red, green, & blue
        :return: None
        """
        self.set_colors([False, False, False])
        self.turn_on()

    def turn_off(self):
        """
        turns the led off
        :return: None
        """
        self.set_colors([True, True, True])
        self.turn_on()

    # noinspection PyProtectedMember
    @staticmethod
    def _flasher(color_led):
        """
        this callback changes the led to be off if it is on, and on if it is off.  It is called once and runs in a loop.
        :param color_led: the led to be flashed
        :return: None
        """
        on = True
        original_colors = color_led.colors
        print("starting flasher loop with {} {} {}".format(color_led.colors,
                                                           color_led.on_off,
                                                           threading.get_ident()))
        if color_led._flasher_running:
            print('already flashing!')
            return
        color_led._flashing = True
        color_led._flasher_running = True
        while color_led._flashing:
            if on:
                color_led.set_colors(original_colors)
                color_led.turn_on()
                time.sleep(color_led.on_off[0] / 1000)
            else:
                color_led.turn_off()
                time.sleep(color_led.on_off[1] / 1000)
            on = not on
        color_led._flasher_running = False
        print("exiting flasher loop with {} {} {}".format(color_led.colors,
                                                          color_led.on_off,
                                                          threading.get_ident()))

    def start_flashing(self, on_off):
        """
        starts the color led flashing
        :param on_off: time (milliseconds) the led is [on, off]
        :return: None
        """
        self.on_off = on_off
        WorkerThread(callback_function=self._flasher, parameters=self).start()

    def stop_flashing(self, fast_return=False):
        """
        stops the flashing LED and waits until it is done flashing.
        NOTE that this will pause execution until the current flash tops or fast_return is True
        :return: None
        """
        self._flashing = False  # stop flashing
        while not fast_return and self._flasher_running:
            time.sleep(.01)


class ButtonLightSequence:
    @staticmethod
    def callback(pin, current_state, button_light_sequence):
        """
        Callback when the button is pressed down
        :param current_state: not used
        :param pin: not used
        :param button_light_sequence: the ButtonLightSequence
        :return: None
        """
        print("button pressed down")
        button_light_sequence.stepping = True
        while button_light_sequence.stepping:
            button_light_sequence.state_light.state_stepper()
            print("sleeping for {}".format(button_light_sequence.time_between_states / 1000))
            time.sleep(button_light_sequence.time_between_states / 1000)

    def __init__(self, callback, button_pin, states, time_between_states=1000):
        """
        A ButtonLightSequence starts a sequence when the button is pressed.  As the button remains pressed down, the
        sequence continues.  When the  button is released, the sequence is stopped and the callback is called.
        :param callback: callback to call when the button is released
        :param button_pin: pin the button is on
        :param states: list of StateLight.States
        """
        self.callback = callback
        self.button = Button(pin=button_pin, callback=ButtonLightSequence.callback, package=self)
        self.state_light = StateLight(states)
        self.time_between_states = time_between_states
        self.stepping = False


class StateLight:
    class State:
        def __init__(self, light, duration=0, colors=None, on_off=None, package=None):
            """
            A StateLight.State is a state of an individual light.  It can be an Led, ColoredLed, or a FlashingLed.
            :param light: the light for this state
            :param duration: the duration it will be on this state.  Don't use this parameter if you are going to call
            state_stepper manually
            :param on_off: the time the led will be [on, off] in milliseconds
            :param colors: the array of colors if this is a ColoredLed
            """
            if colors is None:
                colors = []
            self.light = light
            self.duration = duration
            self.colors = colors
            self.on_off = on_off
            self.package = package

    def __init__(self, state_list):
        """
        Initializes a StateLight which is one or more LEDs defined by StateLight.States
        :param state_list: array of all of the StateLight.States
        """
        self.state_list = state_list
        self.stepper_worker_thread = None
        self.state = 0

    def state_stepper(self):
        """
        Steps to the next state of the light(s)
        :return: None
        """
        # activate the state
        state = self.state_list[self.state]
        # test if goes in loop
        if isinstance(state.light, FlashingLed):
            state.light.start()
        elif isinstance(state.light, Led):
            state.light.toggle(True)
        elif isinstance(state.light, ColorLed):
            state.light.stop_flashing()
            state.light.set_colors(state.colors)
            state.light.start_flashing(on_off=state.on_off)
        time.sleep(state.duration)
        # advance the counter
        if self.state >= len(self.state_list) - 1:
            self.state = 0
        else:
            self.state += 1
        # turn off the state
        if isinstance(state.light, FlashingLed):
            state.light.stop()
            while state.light.state:
                time.sleep(.01)
        elif isinstance(state.light, Led):
            state.light.toggle(new_state=False)

    def start(self):
        """
        Starts the StateLight so that it will automatically go through all of the states
        :return: None
        """
        if self.stepper_worker_thread is None:
            self.stepper_worker_thread = WorkerThread(self.state_stepper)
            self.stepper_worker_thread.start()

    def stop(self):
        """
        Stops the StateLight
        :return:
        """
        if self.stepper_worker_thread is not None:
            self.stepper_worker_thread.stop_flashing()
            self.stepper_worker_thread = None
        for state in self.state_list:
            if isinstance(state.light, FlashingLed):
                state.light.stop()
            elif isinstance(state.light, Led):
                state.light.toggle(new_state=False)

    def get_state(self):
        """
        Gets the current StateLight.State and if it is running
        :return: current StateLight.State, True/False
        """
        return self.state, self.is_running

    # noinspection PyProtectedMember
    def is_running(self):
        """
        Gets if the thread for this StateLight is running
        :return: True/False if the Statelight is running
        :return: True/False if the Statelight is running
        """
        if self.stepper_worker_thread is None:
            return False
        else:
            return self.stepper_worker_thread._is_running


class TemperatureHumidity:
    class SensorType(Enum):
        """
        Defines the sensor type
        """
        AM2302 = 0

    class Values:
        def __init__(self, temperature, humidity):
            """
            Values recorded at the specified time
            :param temperature: Temperature recorded
            :param humidity: Humidity recorded
            """
            self.time_stamp = datetime.datetime.now()
            self.temperature = temperature
            self.humidity = humidity
            self.worker_thread = None

    @staticmethod
    def _get_data_thread(temp_humidity):
        """
        This function is  continuously called to get data from the sensor.  It fills the queue with Values
        :param temp_humidity: this is the calling object (self)
        :return: None
        """
        logger = get_logger()
        humidity, temperature = Adafruit_DHT.read_retry(temp_humidity.sensor_type, temp_humidity.pin)
        if temp_humidity.queue.full():
            logger.critical('Temperature and Humidity queue is full')
            return
        if humidity is not None and temperature is not None:
            if not temp_humidity.centigrade:
                temperature = 9.0 / 5.0 * temperature + 32
            logger.debug("pin:{}, temp:{}, humidity:{}".format(temp_humidity.pin, temperature, humidity))
            temp_humidity.queue.put(TemperatureHumidity.Values(temperature, humidity))

    def __init__(self, pin, sensor_type, centigrade=False):
        """
        Initializes a TemperatureHumidity sensor
        :param pin: Pin the sensor is on
        :param sensor_type: Type of sensor (see TemperatureHumidity.SensorType)
        :param centigrade: Set to True if you want centigrade values
        """
        self.pin = pin
        self.queue = Queue(1000)
        self.centigrade = centigrade
        if sensor_type == TemperatureHumidity.SensorType.AM2302:
            self.sensor_type = Adafruit_DHT.AM2302
        else:
            raise RuntimeError('Invalid Sensor Type')
        self.worker_thread = None

    def start(self):
        """
        This method starts the thread to read data from the sensor.  Note that it may take some time to stabilize
        """
        if self.worker_thread and self.worker_thread.is_running():
            return

        # empty the queue
        while not self.queue.empty():
            self.queue.get_nowait()
        self.worker_thread = WorkerLoopThread(callback_function=self._get_data_thread, parameters=self)
        self.worker_thread.start()

    def stop(self):
        """
        This method stops the thread.
        """
        if self.worker_thread and self.worker_thread.is_running():
            self.worker_thread.stop()
            self.worker_thread = None

    def is_running(self):
        """
        Indicates if the thread is running
        :return: True if the data collection thread is running
        """
        return self.worker_thread and self.worker_thread.is_running()


class VibrationSensor:
    class Runner(threading.Thread):
        def __init__(self, parent_sensor):
            super(VibrationSensor.Runner, self).__init__()
            self.parent = parent_sensor
            logger = get_logger()
            logger.debug("creating a VibrationSensor.Runner")
            self._is_running = False
            self.jitter = 1000  # 1 mS
            self.changed_time = None
            self.changed_state = False
            self.last_time = datetime.datetime.now()

        def run(self):
            logger = get_logger()
            logger.debug("starting VibrationSensor.Runner")
            self._is_running = True
            while self._is_running:
                if self.changed_time is not None:
                    time_delay = (self.changed_time - self.last_time).microseconds
                    self.last_time = self.changed_time
                    logger.critical("delay:{}".format(time_delay))
                    if time_delay > self.jitter:
                        logger.critical("moving")

        # noinspection PyUnusedLocal
        def state_change(self, pin):
            get_logger().critical("called")
            self.changed_state = datetime.datetime.now()

    def __init__(self, pin, callback):
        self.pin = pin
        self.callback_function = callback
        self.thread = None
        self.last_change = datetime.datetime.now()
        self.last_state = False
        self.runner = None

    def start(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN)
        self.runner = VibrationSensor.Runner(self)
        self.runner.start()
        GPIO.add_event_detect(self.pin, GPIO.RISING, bouncetime=1)
        GPIO.add_event_callback(self.pin, self.runner.state_change)

    def _vibration_detected(self, pin):
        logger = get_logger()
        time_now = datetime.datetime.now()
        current_state = GPIO.input(pin)
        logger.critical("called:{}, {}, {}, {}".format(current_state, time_now, self.last_change,
                                                       (time_now - self.last_change).microseconds))
        if current_state != self.last_state:
            if (time_now - self.last_change).microseconds > 1000:
                logger.critical("time exceeded")
                if current_state:
                    logger.critical("movement")
                else:
                    logger.critical("no movement")
                self.last_state = current_state
                self.last_change = time_now


class Accelerometer:
    # ADXL345 constants
    EARTH_GRAVITY_MS2 = 9.80665
    SCALE_MULTIPLIER = 0.004

    DATA_FORMAT = 0x31
    BW_RATE = 0x2C
    POWER_CTL = 0x2D

    BW_RATE_1600HZ = 0x0F
    BW_RATE_800HZ = 0x0E
    BW_RATE_400HZ = 0x0D
    BW_RATE_200HZ = 0x0C
    BW_RATE_100HZ = 0x0B
    BW_RATE_50HZ = 0x0A
    BW_RATE_25HZ = 0x09

    RANGE_2G = 0x00
    RANGE_4G = 0x01
    RANGE_8G = 0x02
    RANGE_16G = 0x03

    MEASURE = 0x08
    AXIS_DATA = 0x32

    address = None

    def __init__(self, address=0x53,
                 bandwidth_rate_flag=BW_RATE_100HZ, range_flag=RANGE_2G):
        self.address = address
        if pio_loaded:
            # select the correct i2c bus for this revision of Raspberry Pi
            revision = ([line[12:-1]
                         for line in open('/proc/cpuinfo', 'r').readlines()
                         if line[:8] == "Revision"] + ['0000'])[0]
            self.bus = smbus.SMBus(1 if int(revision, 16) >= 4 else 0)
        self.bus.write_byte_data(self.address, Accelerometer.BW_RATE, bandwidth_rate_flag)
        value = self.bus.read_byte_data(self.address, Accelerometer.DATA_FORMAT)
        value &= ~0x0F
        value |= range_flag
        value |= 0x08
        self.bus.write_byte_data(self.address, Accelerometer.DATA_FORMAT, value)
        self.bus.write_byte_data(self.address, Accelerometer.POWER_CTL, Accelerometer.MEASURE)

    def get_axis(self, g_force=False):
        data = self.bus.read_i2c_block_data(self.address, Accelerometer.AXIS_DATA, 6)
        now = datetime.datetime.now()
        x = data[0] | (data[1] << 8)
        if x & (1 << 16 - 1):
            x -= 1 << 16
        y = data[2] | (data[3] << 8)
        if y & (1 << 16 - 1):
            y -= 1 << 16
        z = data[4] | (data[5] << 8)
        if z & (1 << 16 - 1):
            z -= 1 << 16
        if g_force:
            x *= Accelerometer.SCALE_MULTIPLIER
            y *= Accelerometer.SCALE_MULTIPLIER
            z *= Accelerometer.SCALE_MULTIPLIER
        else:
            x *= Accelerometer.EARTH_GRAVITY_MS2
            y *= Accelerometer.EARTH_GRAVITY_MS2
            z *= Accelerometer.EARTH_GRAVITY_MS2
        x = round(x, 4)
        y = round(y, 4)
        z = round(z, 4)
        return {"x": x, "y": y, "z": z, "time": now}


class Motor:
    def __init__(self, accelerometer, resting_values):
        self.accelerometer = accelerometer
        self.resting_values = resting_values
        self.movement_checker = None
        self.motor_running = False

    class MovementChecker(threading.Thread):
        check_frequency = .001
        value_count = 10

        def __init__(self, parent_motor, callback):
            super(Motor.MovementChecker, self).__init__()
            self.callback = callback
            self.parent_motor = parent_motor
            self.thread_is_running = False
            self.values = [{"x": None, "y": None, "z": None}] * self.value_count

        def run(self):
            last_entry = 0
            filled = False
            resting_called = running_called = False
            while self.thread_is_running:
                # keep the counter within this thread's internal buffer
                if last_entry == len(self.values) - 1:
                    last_entry = 0
                    filled = True
                else:
                    last_entry += 1
                self.values[last_entry] = self.parent_motor.accelerometer.get_axis(True)
                if filled:  # no checking occurs until the small array is filled with movement data
                    if self.is_resting():
                        self.parent_motor.motor_running = False
                        if not resting_called:  # have not called stopped callback
                            running_called = False
                            resting_called = True
                            threading.Thread(target=self.callback, args=(False, self.when_event_occurred()))
                    else:  # motor is moving
                        self.parent_motor.motor_running = True
                        if not running_called:  # have not called callback
                            running_called = True
                            resting_called = False
                            threading.Thread(target=self.callback, args=(True, self.when_event_occurred()))
                time.sleep(Motor.MovementChecker.check_frequency)

        def is_resting(self):
            avg_x = avg_y = avg_z = 0
            for value in self.values:
                avg_x += value["x"]
                avg_y += value["y"]
                avg_z += value["z"]
            avg_x /= len(self.values)
            avg_y /= len(self.values)
            avg_z /= len(self.values)
            if avg_x > self.parent_motor.resting_values["x"] or \
                    avg_y > self.parent_motor.resting_values["y"] or \
                    avg_z > self.parent_motor.resting_values["z"]:
                return True
            else:
                return False

        def when_event_occurred(self):
            for value in self.values:
                if self.parent_motor.motor_running:  # look for when the motor first started moving
                    if value["x"] > self.parent_motor.resting_values["x"] or \
                            value["y"] > self.parent_motor.resting_values["y"] or \
                            value["z"] > self.parent_motor.resting_values["z"]:
                        return value["time"]
                else:  # look for when the motor first stopped moving
                    if value["x"] < self.parent_motor.resting_values["x"] or \
                            value["y"] < self.parent_motor.resting_values["y"] or \
                            value["z"] < self.parent_motor.resting_values["z"]:
                        return value["time"]

    def start(self, callback):
        Motor.MovementChecker(self, callback).start()

    @staticmethod
    def get_resting_values(accelerometer, duration_in_mils):
        start_time = datetime.datetime.now()
        min_x = min_y = min_z = sys.float_info.max
        max_x = max_y = max_z = 0
        while True:
            values = accelerometer.get_axis(True)
            if values["x"] > max_x:
                max_x = values["x"]
            if values["x"] < min_x:
                min_x = values["x"]
            if values["y"] > max_y:
                max_y = values["y"]
            if values["y"] < min_y:
                min_y = values["y"]
            if values["z"] > max_z:
                max_z = values["z"]
            if values["z"] < min_z:
                min_z = values["z"]
            if (datetime.datetime.now() - start_time).total_seconds() * 1000 >= duration_in_mils:
                break
            time.sleep(.001)

        return {"x": {"max": max_x, "min": min_x},
                "y": {"max": max_y, "min": min_y},
                "z": {"max": max_z, "min": min_z}
                }

    def is_moving(self):
        return self.motor_running
