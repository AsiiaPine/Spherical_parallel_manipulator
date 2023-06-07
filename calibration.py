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


class Calibration():
    axes = {0: "x", 1: "y", 2: "z"}

    def calibrate(self, xyz):
        result = self.curr_calib.update(xyz)
        if result is not None:
            new_offset = self.calibs[self.axis].offsets_of_axis
            self.axis +=1
            self.curr_calib = self.calibs[self.axis]
            self.curr_calib.offsets_of_axis = new_offset
            if self.axis ==2:
                return "Calibration succed and over"
        return None

    def __init__(self, n_measurements=1000) -> None:
        self.n_measurements = n_measurements
        self.offsets = [0, 0, 0]
        self.calib_x = Calibration_by_axis(axis=0)
        self.calib_y = Calibration_by_axis(axis=1)
        self.calib_z = Calibration_by_axis(axis=2)
        self.calibs = [self.calib_x, self.calib_y, self.calib_z]
        self.axis = 0
        self.curr_calib = self.calib_x


class Calibration_by_axis():
    def __init__(self, axis, n_measurements=1000, offsets_of_axis=[0, 0, 0]) -> None:
        self.axis = axis
        self.coeff = 1
        self.mean_val = 0
        self.array = []
        self.n_measurements = n_measurements
        self.i = 0
        self.offsets_of_axis = [0, 0, 0] + offsets_of_axis

    def update(self, xyz):
        if self.i < self.n_measurements:
            self.array.append(xyz)
            return None
        
        elif self.i == self.n_measurements:
            self.mean_val = np.mean(self.array[self.axis]) - \
                self.offsets_of_axis[self.axis]
            array = np.array(self.array)

            i = 0
            if i != self.axis:
                self.offsets_of_axis[i] = max(np.mean(array[:, i], axis=0), self.offsets_of_axis[i])
            print("Calibration complete")
            return "Calibration complete"


serialPort = serial.Serial(
    port='/dev/ttyUSB0', baudrate=115200)  # open serial port
print(serialPort.name)  # check which port was really used

input_array = []

axes = {"x": 0, "y": 1, "z": 2}

calibration = Calibration()
axis = "z"
try:
    while (1):
        # Wait until there is data waiting in the serial buffer
        if (serialPort.in_waiting > 0):
            # Read data out of the buffer until a carraige return / new line is found
            serialString = serialPort.readline()

            # Print the contents of the serial data
            print(serialString.decode('Ascii'))

            input_array.append(
                list(map(int, serialString.decode('Ascii').split())))
            
            get_imu = lambda x : "1" in x
            imu_1_headers = filter(get_imu, headers)
            
            calibration.calibrate(input_array[-1])
            # Tell the device connected over the serial port that we recevied the data!
            # The b at the beginning is used to indicate bytes!
            # serialPort.write(b"Thank you for sending data \r\n")

except:
    serialPort.close()  # close port
    a = np.asarray(input_array)
    np.savetxt("imu_results_16.csv", a, delimiter=";",
               header=";".join(headers))

    # df = pd.read_csv("imu_results.csv", delimiter=";")  # will be used in future work with big data
    # print(df.head())
