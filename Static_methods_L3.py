import time
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_analog_in_v3 import BrickletAnalogInV3
from pynput import keyboard


class methods():
    @staticmethod
    def setup(UID_analog_in:str):
        # sets up IP connections to the stepper and analog in bricklet and sets default configurations
        HOST = "localhost"
        PORT = 4223

        # Create Tinkerforge objects
        ipcon = IPConnection()

        analog_in = BrickletAnalogInV3(UID_analog_in, ipcon)

        ipcon.connect(HOST, PORT)
        # Don't use device before ipcon is connected

        return ipcon, analog_in
    
    @staticmethod
    def shut_down(ipcon, ser:list):
        ipcon.disconnect() # disconnect IP Connection
        for i in ser:
            methods.send_ser_msg(i, b"SOUT0\r")
            i.close()

    @staticmethod
    def send_ser_msg(ser, msg):
        rec_count = 0
        ok_received = False

        ser.write(msg) # send serial command
        while ok_received == False: 
            # this loop checks for the OK\r that in this case the manson returns
            # this breaks for other devices that don't send OK\r as an answer or if they send data, that
            # data will be lost when using this function
            start = time.perf_counter()
            returned_msg = []
            while returned_msg[-1:] != [b"\r"] and time.perf_counter() - start < 10:
                # reads serial receive buffer (bad implementation of serial.readline())
                returned_msg.append(ser.read())
                t = time.perf_counter()
            
            if b"O" in returned_msg and b"K" in returned_msg: # checks if the received message is an ok
                print("OK received!")
                ok_received = True
                return None
            returned_msg = []
            rec_count += 1

            if rec_count > 3: # raise an error if the three lines after a command don't inlcude an OK\r
                raise TimeoutError("No OK received")
            
    @staticmethod
    def manson_init(ser): # send necessary commands to initiate communication with manson
        methods.send_ser_msg(ser, b"SABC3\r")
        methods.send_ser_msg(ser, b"ENDS\r")
        methods.send_ser_msg(ser, b"SOCP0100\r")
        methods.send_ser_msg(ser, b"SOUT1\r")

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