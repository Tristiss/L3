import serial
import time

port = "COM7"

ser = serial.Serial(port, baudrate = 9600)

def send_ser_msg(ser, msg):
    rec_count = 0
    ok_received = False
    ser.write(msg)
    while ok_received == False:
        start = time.perf_counter()
        returned_msg = []
        while returned_msg[-1:] != [b"\r"] and time.perf_counter() - start < 10:
            returned_msg.append(ser.read())
            print(returned_msg)
            t = time.perf_counter()
        
        if b"O" in returned_msg and b"K" in returned_msg:
            print("OK received!")
            ok_received = True
            return None
        returned_msg = []
        rec_count += 1

        if rec_count > 3:
            raise TimeoutError("No OK received")

while True:
    msg = input("Enter switch: ")

    match msg:
        case "close":
            break
        case "0":
            msg = msg.encode() + b"\r"
            send_ser_msg(ser, msg)
        case _:
            pass

ser.close()