import numpy as np
import threading
from Static_methods_L3 import *

port = "COM6"
UID_analog_in = "27hk"


def measurement():
    pass

def measurement_row():
    pass

flag = threading.Event()
monitor = threading.Thread(methods.monitor, daemon = True)

def main():
    ipcon, analog_in, ser = methods.setup(port, UID_analog_in)

    measure = threading.Thread(measurement_row)
    measure.start()

    try:
        measure.join()
    except:
        methods.shut_down(ipcon, ser)
        print("Measurement failed")
    finally:
        methods.shut_down(ipcon, ser)

if __name__ == "__main__":
    main()