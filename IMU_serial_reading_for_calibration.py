import serial
import numpy as np
import pandas as pd
import time

from datetime import datetime

headers = [
    "Timestamp",
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
df = pd.DataFrame(columns=headers)
print('len(df)', len(df))
try:
    while True:
        if serialPort.in_waiting > 0:
            serialString = serialPort.readline().decode('ascii').strip()

            named_tuple = time.localtime() # get struct_time
            # timestamp = time.strftime("%H:%M:%S:%f", named_tuple)[:-3]
            timestamp = datetime.now().strftime("%H:%M:%S:%f")[:-3]
            print(f"{timestamp}: {serialString}")
            data = [timestamp]
            #for i in list(map(int, serialString.split())):
             #   data.append(i)
            data = [timestamp] + list(map(int, serialString.split()))
            input_array.append(data)
            df.loc[len(df)] = data

except KeyboardInterrupt:
    serialPort.close()  # close port
    a = np.asarray(input_array)
    np.savetxt("imu_results.csv", a, delimiter=";", header=";".join(headers), fmt='%s')
    df.to_csv("imu_results.csv", sep=";", index=False)
    df = pd.read_csv("imu_results.csv", delimiter=";")
    print(df.head())