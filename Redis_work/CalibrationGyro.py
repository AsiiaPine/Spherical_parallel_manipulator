import json
import asyncio

from Motor.libs.interface import CanBus
from Motor.libs.gyems import Gyems
from RedisWorker import AsyncRedisWorker
from CalibrationAccel import Calibration, CalibrationByAxis


class CalibrationGyro(Calibration):
    def __init__(self, n_measurements=1000, omegas=[10], to_show_progress=False) -> None:
        """
        The class is used to calibrate IMU, you have to attach the imu to motor and calibrate it with different axes and speeds. The instance connects to the motor via CAN and controls its speed.
        """
        super().__init__(n_measurements)
        
        self.gyr_calib_x = CalibrationGyroByAxis(
            axis=0, n_measurements=n_measurements, to_show_progress=to_show_progress)
        self.gyr_calib_y = CalibrationGyroByAxis(
            axis=1, n_measurements=n_measurements, to_show_progress=to_show_progress)
        self.gyr_calib_z = CalibrationGyroByAxis(
            axis=2, n_measurements=n_measurements, to_show_progress=to_show_progress)
        self.calibs = [self.gyr_calib_x, self.gyr_calib_y, self.gyr_calib_z]
        self.to_show_progress = to_show_progress
        self.curr_calib = self.gyr_calib_x
        self.omega_counter = 0

        self.omegas = omegas
        print(
            f"Press ENTER to start calibrate gyroscope around the {self.axes[self.axis]} axis")
        input()

    def calibrate(self, xyz):
        try:
            result = super().calibrate(xyz)
            if result == 1:
                print(
                    f"Calibration is complete for all omegas.\nChange Axis to {self.axes[self.axis]}\nPrint *yes* when you will be ready, or *no* to stop the process")
                is_ready = input()
                while (not "yes" in is_ready):
                    if "no" in is_ready:
                        print("Process stops")
                        raise KeyboardInterrupt
                    is_ready = input()
            return result

        except:
            return 1


class CalibrationGyroByAxis(CalibrationByAxis):
    def __init__(self, axis, n_measurements=1000, offsets_of_axis=..., to_show_progress=False) -> None:
        super().__init__(axis, n_measurements, offsets_of_axis, to_show_progress)
        self.coeffs = []

    def update_speed(self):
        print("Enter new motor speed")
        string = input()
        if string.isnumeric():
            self.omega = float(string)
        else:
            print(f"Error: {string} is not a number")
            self.update_speed()

    def update(self, xyz):
        result = super().update(xyz)
        self.coeff = self.coeff/self.omega
        self.coeffs.append(self.coeff)
        to_change_speed = input()
        if "yes" in to_change_speed:
            to_change_speed = True

        if result == 1 and to_change_speed:
            self.update_speed()
            return 0
        return result

def load_data_from_json(key_str: int|str):
    try:
        with open('motor_speeds.json') as f:
            motor_tests = json.loads(json.load(f))
        for key, val in motor_tests.items():
            if str(key_str) in key:
                motor_tests = val
                return motor_tests
            raise ValueError(f'tests_data do not have such word in keys {key_str}')
        return {}
    except ValueError:
        print(f'tests_data do not have such word in keys {key_str}')
        return {}


async def main():
    calibration_gyr = CalibrationGyro()

    imu_n = 1
    calib_data= load_data_from_json(imu_n)
    print(calib_data)

    if calib_data == {}:
        print("there is no data for the gyro calibration in 'motor_speeds.json' file.")
        return
    worker = AsyncRedisWorker()

    calibration_gyr_1 = CalibrationGyro(
        n_measurements=1000, to_show_progress=True)
    async for message in worker.subscribe(count=10000):
        if calibration_gyr_1.calibration_is_finished:
            break
        calibration_gyr_1.calibrate(message.imu_1.acc)


if __name__ == '__main__':

    asyncio.run(main())