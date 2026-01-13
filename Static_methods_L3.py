import time
import serial
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_analog_in_v3 import BrickletAnalogInV3
from pynput import keyboard


class methods():
    @staticmethod
    def setup(serial_port:str, UID_analog_in:str):
        # sets up IP connections to the stepper and analog in bricklet and sets default configurations
        HOST = "localhost"
        PORT = 4223

        # Create Tinkerforge objects
        ipcon = IPConnection()

        analog_in = BrickletAnalogInV3(UID_analog_in, ipcon)

        ipcon.connect(HOST, PORT)
        # Don't use device before ipcon is connected

        ser = serial.Serial(serial_port, baudrate = 9600)

        return ipcon, analog_in, ser
    
    @staticmethod
    def shut_down(ipcon, ser):
        ipcon.disconnect() # disconnect IP Connection
        ser.close()

    @staticmethod
    def check_for_ok(ser):
        time.sleep(0.01)
        start = time.perf_counter()
        t = 0
        while ser.read() not in [b"OK\r", b"OK\r\n", b"OK\n", b"O", b"K", b"\r"] or t > 5:
            time.sleep(0.01)
            t = time.perf_counter() - start
            if t > 5:
                raise Exception("No response to serial command")
        print("Checked")

    @staticmethod
    def monitor(flag):
        # this function is a daemon thread that raises a flag that the measurment and calibration loops look out for
        pressed_keys = set()
        def on_press(key):
            # checks if the pressed key is the Escape button
            pressed_keys.add(key)
            if keyboard.Key.esc in pressed_keys:
                print("Esc detected! Stopping measurement...")
                flag.set()  # Signal measurement thread to stop

        def on_release(key):
            # released keys are being deleted from the set of pressed keys
            pressed_keys.discard(key)

        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()  # Blocks until shutdown