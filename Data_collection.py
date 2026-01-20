import time
import threading
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from tinkerforge.bricklet_analog_in_v3 import BrickletAnalogInV3

from Static_methods_L3 import *

voltages = np.linspace(20, 50, 100)
reverse_bias = np.linspace(0, 5, 50)

port = "COM6"
UID_analog_in = "27hk"

num = 13

def set_voltage(ser, volt):
    # volt [V]
    volt = int(volt * 100) # convert V to mV
    msg = f"VOLT3{volt:04d}\r"
    methods.send_ser_msg(ser, msg.encode())
    print(msg[5:])
    time.sleep(0.5)
    if volt == 0:
        time.sleep(9)

def main():
    ipcon, analog_in, ser = methods.setup(port, UID_analog_in)

    ser_reverse_bias = serial.Serial("COM5", baudrate = 9600)

    analog_in.set_oversampling(BrickletAnalogInV3.OVERSAMPLING_16384)

    methods.send_ser_msg(ser, b"SABC3\r")
    methods.send_ser_msg(ser, b"ENDS\r")
    methods.send_ser_msg(ser, b"SOCP0100\r")
    methods.send_ser_msg(ser, b"SOUT1\r")

    methods.send_ser_msg(ser_reverse_bias, b"SABC3\r")
    methods.send_ser_msg(ser_reverse_bias, b"ENDS\r")
    methods.send_ser_msg(ser_reverse_bias, b"SOCP0100\r")
    methods.send_ser_msg(ser_reverse_bias, b"SOUT1\r")

    flag = threading.Event()
    monitor_thread = threading.Thread(target = methods.monitor, args = [flag,], daemon = True)
    monitor_thread.start()

    def measure():
        for j in reverse_bias:
            data = []
            set_voltage(ser_reverse_bias, j)
            for i in voltages:
                set_voltage(ser, i)
                mes_volt = analog_in.get_voltage()
                time.sleep(0.5)
                print(mes_volt)
                data.append(mes_volt)
                if flag.is_set() == True:
                    return None
            df = pd.DataFrame({"voltages": voltages[:len(data)], "currents": data})
            df.to_csv(fr"C:\Programmieren\Praktikum\L3\Data\Messung_rev_bias_{j}_{num}.csv", sep = ";")
            plt.plot(df["voltages"], df["currents"])
            set_voltage(ser, 0)

    measure_thread = threading.Thread(target = measure)
    measure_thread.start()

    try:
        measure_thread.join()
    except:
        pass
    else:
        set_voltage(ser, 0)
    finally:
        methods.shut_down(ipcon, ser)

    plt.show()

if __name__ == "__main__":
    main()