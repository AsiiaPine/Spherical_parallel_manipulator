import serial
import numpy as np
import pandas as pd

headers = [
    "imu_1_accel x",
    "imu_1_accel y",
    "imu_1_accel z",
    "imu_1_gyro x",
    "imu_1_gyro y",
    "imu_1_gyro z",
    "imu_2_accel x",
    "imu_2_accel y",
    "imu_2_accel z",
    "imu_2_gyro x",
    "imu_2_gyro y",
    "imu_2_gyro z",
]

serialPort = serial.Serial(port='/dev/ttyUSB0', baudrate=115200)  # open serial port
print(serialPort.name)  # check which port was really used

input_array = []
try:
    while (1):

        # Wait until there is data waiting in the serial buffer
        if (serialPort.in_waiting > 0):
            # Read data out of the buffer until a carraige return / new line is found
            serialString = serialPort.readline()

            # Print the contents of the serial data
            print(serialString.decode('Ascii'))
            input_array.append(list(map(int, serialString.decode('Ascii').split())))
            # Tell the device connected over the serial port that we recevied the data!
            # The b at the beginning is used to indicate bytes!
            # serialPort.write(b"Thank you for sending data \r\n")
except:
    serialPort.close()  # close port
    a = np.asarray(input_array)
    np.savetxt("imu_results.csv", a, delimiter=";", header=";".join(headers))
    df = pd.read_csv("imu_results.csv", delimiter=";")  # will be used in future work with big data
    print(df.head())
