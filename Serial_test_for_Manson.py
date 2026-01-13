import time
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from tinkerforge.bricklet_analog_in_v3 import BrickletAnalogInV3

from Static_methods_L3 import *

voltages = np.linspace(20, 50, 100)

port = "COM6"
UID_analog_in = "27hk"

num = 5

data =[]
mes_voltages = []

def set_voltage(volt):
    # volt [V]
    volt = int(volt * 100) # convert V to mV
    msg = f"VOLT3{volt:04d}\r"
    ser.write(msg.encode())
    print(msg[5:])
    mes_voltages.append(msg[5:])
    methods.check_for_ok(ser)
    time.sleep(1)
    if volt == 0:
        time.sleep(10)

ipcon, analog_in, ser = methods.setup(port, UID_analog_in)

analog_in.set_oversampling(BrickletAnalogInV3.OVERSAMPLING_16384)

ser.write(b"SABC3\r")
methods.check_for_ok(ser)
ser.write(b"ENDS\r")
methods.check_for_ok(ser)
ser.write(b"SOCP0100\r")
methods.check_for_ok(ser)

ser.write(b"SOUT1\r")
methods.check_for_ok(ser)

for i in voltages:
    set_voltage(i)
    mes_volt = analog_in.get_voltage()
    time.sleep(0.5)
    print(mes_volt)
    data.append(mes_volt)

set_voltage(0)

ser.write(b"SOUT0\r")

methods.shut_down(ipcon, ser)

df = pd.DataFrame(data, index = voltages)

df.to_csv(fr"C:\Programmieren\Praktikum\L3\Messung_{num}.csv", sep = ";")

df.plot()

plt.show()