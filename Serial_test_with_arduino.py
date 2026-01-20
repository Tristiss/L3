import serial
import time

from Static_methods_L3 import methods

port = "COM7"

ser = serial.Serial(port, baudrate = 9600)

while True:
    msg = input("Enter switch: ")

    match msg:
        case "close":
            break
        case "0":
            msg = msg.encode() + b"\r"
            methods.send_ser_msg(ser, msg)
        case _:
            pass

ser.close()