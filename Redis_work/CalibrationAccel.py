import asyncio
import json
import sys
import numpy as np
from RedisWorker import AsyncRedisWorker
from config import headers, acc_coeffitients_str, acc_offsets_str


class CalibrationByAxis():

    def __init__(self, axis, n_measurements=1000, offsets_of_axis=[100000, 100000, 10000], to_show_progress=False) -> None:
        self.axis = axis
        self.coeff = 1
        self.mean_val = 0
        self.array = []
        self.n_measurements = n_measurements
        self.i = 0
        self.offsets_of_axis = offsets_of_axis
        self.to_show_progress = to_show_progress
        self.point = n_measurements/100
        self.increment = n_measurements/10

    def show_progress(self):
        sys.stdout.write('\r')
        # the exact output you're looking for:
        sys.stdout.write("\r[" + "=" * int(self.i / self.increment) + " " * int(
            (self.n_measurements - self.i) / self.increment) + "]" + str(self.i / self.point) + "%")
        sys.stdout.flush()

    def update(self, xyz):
        if self.to_show_progress:
            self.show_progress()
        if self.i < self.n_measurements:
            self.array.append(xyz)
            self.i += 1
            # n iterations less that the desired one
            return 0

        elif self.i == self.n_measurements:
            mean_val = np.mean(self.array[self.axis]) - \
                self.offsets_of_axis[self.axis]
            array = np.array(self.array)
            self.coeff = mean_val

            i = 0
            while (i < 3):
                if i != self.axis:
                    mean_i = abs(np.mean(array[:, i], axis=0))
                    # changes > to < and made default offset != 0, 0, 0
                    if mean_i < abs(self.offsets_of_axis[i]):
                        self.offsets_of_axis[i] = np.mean(array[:, i], axis=0)
                i += 1
            # print("self.offsets_of_axis", self.offsets_of_axis)
            # calibration complete
            return 1


class Calibration():
    """
    Abstract class which can be used for calibration
    """

    def __init__(self, n_measurements=1000) -> None:
        self.axes = ["x", "y", "z"]
        self.n_measurements = n_measurements
        self.offsets = [0, 0, 0]

        self.gyr_calib_complete = False
        self.axis = 0
        self.curr_calib = CalibrationByAxis(0)
        self.calibs = []
        self.calibration_is_finished = False
        self.first_stage_of_calib_is_finished = False

    def update_axis(self):
        self.curr_calib = self.calibs[self.axis]

    def calibrate(self, xyz):
        """
        The function is used to set new data and get calibration parameters for each axis.
        Use self.calibration_is_finished to check if the calibration is finished.
        """
        result = self.curr_calib.update(xyz)
        if result:  # calibration around axis is comlete
            self.update_axis()
            self.offsets = self.curr_calib.offsets_of_axis
            self.axis += 1
            if self.calibration_is_finished:
                return 1
            return 0  # the calibration around one axis is comlete, change the axis


class CalibrationAcc(Calibration):

    def __init__(self, n_measurements=1000, to_show_progress=False) -> None:
        super().__init__(n_measurements=n_measurements)
        self.acc_calib_x = CalibrationByAxis(
            axis=0, n_measurements=n_measurements, to_show_progress=to_show_progress)
        self.acc_calib_y = CalibrationByAxis(
            axis=1, n_measurements=n_measurements, to_show_progress=to_show_progress)
        self.acc_calib_z = CalibrationByAxis(
            axis=2, n_measurements=n_measurements, to_show_progress=to_show_progress)

        self.__to_show_progress__ = to_show_progress

        self.calibs = [self.acc_calib_x, self.acc_calib_y, self.acc_calib_z]
        self.axis = 0
        self.curr_calib = self.acc_calib_x

        print(
            f"\nPress ENTER to start calibrate accelerometer around the {self.axes[self.axis]} axis")
        input()

    def update_axis(self):
        if self.axis == 3:
            self.axis = 0
            self.first_stage_of_calib_is_finished = True

        if  self.first_stage_of_calib_is_finished:
            if self.axis == 1:
                # calibration is complete. Stop the operation
                self.calibration_is_finished = True
                print("\nCalibration succed and over")
                return 1

            if self.axis == 0 :
                self.acc_calib_x = CalibrationByAxis(
                    axis=0, n_measurements=self.n_measurements, to_show_progress=self.__to_show_progress__)
                self.calibs[0] = self.acc_calib_x
                self.curr_calib = self.calibs[0]
                self.curr_calib.offsets_of_axis = self.offsets

        else:
            return super().update_axis()

    def calibrate(self, xyz):
        result = super().calibrate(xyz)
        if result == 0:
            if self.update_axis() != 1:
                self.curr_calib.offsets_of_axis = self.offsets
                print(
                    f"\nRotate the IMU such as gravity is collinear with {self.axes[self.axis]}")
                print(
                    f"\nPress ENTER to start calibrate around the {self.axes[self.axis]} axis")
                input()
            self.curr_calib.offsets_of_axis = self.offsets


    def get_coeffs(self):
        coeffs = [axis.coeff for axis in self.calibs]
        return coeffs

    def get_offsets(self):
        return self.offsets


async def main():
    calibr_results = {}
    worker = AsyncRedisWorker()

    calibration_acc_1 = CalibrationAcc(
        n_measurements=10, to_show_progress=True)
    async for message in worker.subscribe(count=10000):
        if calibration_acc_1.calibration_is_finished:
            break
        calibration_acc_1.calibrate(message.imu_1.acc)

    print("\n_____\nNext IMU calibration starts!")
    calibration_acc_2 = CalibrationAcc(
        n_measurements=10, to_show_progress=True)
    async for message in worker.subscribe(count=10000):
        if calibration_acc_2.calibration_is_finished:
            break
        calibration_acc_2.calibrate(message.imu_2.acc)

    print("\nCalibration complete")
    acc_offsets_1 = calibration_acc_1.get_offsets()
    acc_coefficients_1 = calibration_acc_1.get_coeffs()

    acc_offsets_2 = calibration_acc_2.get_offsets()
    acc_coefficients_2 = calibration_acc_2.get_coeffs()

    calibr_results = {"imu_1":  {acc_offsets_str: acc_offsets_1, acc_coeffitients_str: acc_coefficients_1}, "imu_2": {
        acc_offsets_str: acc_offsets_2, acc_coeffitients_str: acc_coefficients_2}}
    calib_res_json = json.dumps(calibr_results)

    with open('calib_data.json', 'w+', encoding='utf-8') as f:
        json.dump(calib_res_json, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    asyncio.run(main())