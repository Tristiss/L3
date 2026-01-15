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

def set_voltage(volt):
    # volt [V]
    volt = int(volt * 100) # convert V to mV
    msg = f"VOLT3{volt:04d}\r"
    methods.send_ser_msg(ser, msg.encode())
    print(msg[5:])
    time.sleep(1)
    if volt == 0:
        time.sleep(9)

ipcon, analog_in, ser = methods.setup(port, UID_analog_in)

analog_in.set_oversampling(BrickletAnalogInV3.OVERSAMPLING_16384)

methods.send_ser_msg(ser, b"SABC3\r")
methods.send_ser_msg(ser, b"ENDS\r")
methods.send_ser_msg(ser, b"SOCP0100\r")
methods.send_ser_msg(ser, b"SOUT1\r")

for i in voltages:
    set_voltage(i)
    mes_volt = analog_in.get_voltage()
    time.sleep(0.5)
    print(mes_volt)
    data.append(mes_volt)

set_voltage(0)

methods.shut_down(ipcon, ser)

df = pd.DataFrame(data, index = voltages)

df.to_csv(fr"C:\Programmieren\Praktikum\L3\Messung_{num}.csv", sep = ";")

df.plot()

plt.show()