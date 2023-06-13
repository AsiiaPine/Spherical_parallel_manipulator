import asyncio
import json
import sys
import serial
import numpy as np
import pandas as pd
from redis_worker import AsyncRedisWorker
from Motor.libs import CanBus, Gyems
from config import headers, acc_coeffitients_str, acc_offsets_str


class Calibration_by_axis:
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


class Calibration:
    axes = ["x", "y", "z"]

    def __init__(self, n_measurements=1000) -> None:
        self.n_measurements = n_measurements
        self.offsets = [0, 0, 0]

        self.gyr_calib_complete = False
        self.axis = 0
        self.curr_calib = Calibration_by_axis(0)
        self.calibs = []
        self.calibration_is_finished = False
        self.first_stage_of_calib_is_finished = False

    def calibrate(self, xyz):
        result = self.curr_calib.update(xyz)
        if result:  # calibration around axis is comlete
            self.offsets = self.calibs[self.axis].offsets_of_axis
            self.axis += 1

            if self.axis == 3 and not self.calibration_is_finished:
                self.axis = 0
                self.first_stage_of_calib_is_finished = True

                return 2  # calibrate x axis again

            elif self.axis == 1 and self.first_stage_of_calib_is_finished:
                # calibration is complete. Stop the operation
                self.calibration_is_finished = True

                print("\nCalibration succed and over")
                return 1
            return 0  # the calibration around one axis is comlete, change the axis


class Calibration_acc(Calibration):

    def __init__(self, n_measurements=1000, to_show_progress=False) -> None:
        super().__init__(n_measurements=n_measurements)
        self.acc_calib_x = Calibration_by_axis(
            axis=0, n_measurements=n_measurements, to_show_progress=to_show_progress)
        self.acc_calib_y = Calibration_by_axis(
            axis=1, n_measurements=n_measurements, to_show_progress=to_show_progress)
        self.acc_calib_z = Calibration_by_axis(
            axis=2, n_measurements=n_measurements, to_show_progress=to_show_progress)

        self.__to_show_progress__ = to_show_progress

        self.calibs = [self.acc_calib_x, self.acc_calib_y, self.acc_calib_z]
        self.axis = 0
        self.curr_calib = self.acc_calib_x

        print(
            f"\nPress ENTER to start calibrate accelerometer around the {self.axes[self.axis]} axis")
        input()

    def calibrate(self, xyz):
        result = super().calibrate(xyz)
        if result == 0:
            self.curr_calib = self.calibs[self.axis]
            self.curr_calib.offsets_of_axis = self.offsets
            print(
                f"\nRotate the IMU such as gravity is collinear with {self.axes[self.axis]}")
            print(
                f"\nPress ENTER to start calibrate around the {self.axes[self.axis]} axis")
            input()
            return None

        elif result == 2:
            self.acc_calib_x = Calibration_by_axis(
                axis=0, n_measurements=self.n_measurements, to_show_progress=self.__to_show_progress__)
            self.calibs[0] = self.acc_calib_x
            self.curr_calib = self.calibs[0]
            self.curr_calib.offsets_of_axis = self.offsets
            print(
                f"\nRotate the IMU such as gravity is collinear with {self.axes[0]} again")
            print(
                f"\nPress ENTER to start calibrate around the {self.axes[0]} axis")
            input()

        elif result == 1:
            self.calibration_is_finished = True

    def get_coeffs(self):
        coeffs = [axis.coeff for axis in self.calibs]
        return coeffs

    def get_offsets(self):
        return self.offsets


# class Calibration_gyro(Calibration):
#     def __init__(self, bus: CanBus, motor: Gyems, n_measurements=1000, omegas = [10]) -> None:
#         """
#         The class is used to clibrate IMU, you have to attach the imu to motor and calibrate it with different axes and speeds. The instance connacts to the motor via CAN and controls its speed.
#         """
#         super().__init__(n_measurements)

#         self.gyr_calib_x = Calibration_gyro_by_axis(axis=0, n_measurements=n_measurements)
#         self.gyr_calib_y = Calibration_gyro_by_axis(axis=1, n_measurements=n_measurements)
#         self.gyr_calib_z = Calibration_gyro_by_axis(axis=2, n_measurements=n_measurements)
#         self.calibs = [self.gyr_calib_x, self.gyr_calib_y, self.gyr_calib_z]

#         self.curr_calib = self.gyr_calib_x
#         self.omega_counter = 0

#         self.omegas = omegas
#         self.bus = bus
#         self.motor = motor
#         print(f"Press ENTER to start calibrate guroscope around the {self.axes[self.axis]} axis")
#         input()

#     def disconnect_motor(self):
#         self.motor.disable(True)
#         self.bus.close()

#     def calibrate(self, xyz):
#         try:
#             result = super().calibrate(xyz)
#             if result == 1:
#                 self.motor.disable(True)
#                 self.bus.close()
#                 print(f"Calibration is complete for all omegas.\nChange Axis to {self.axes[self.axis]}\nPrint yes when you will be ready of no to stop process")
#                 is_ready = input()
#                 while (not "yes" in is_ready):
#                     if "no" in is_ready:
#                         print("Process stops")
#                         raise KeyboardInterrupt
#                     is_ready = input()
#             return result

#         except:
#             self.disconnect_motor()
#             print("KeyboardInterrupt, motor disconnected")
#             return 1


# class Calibration_gyro_by_axis(Calibration_by_axis):
#     def __init__(self, axis, n_measurements=1000, offsets_of_axis=[0, 0, 0], motor = None, bus: CanBus = CanBus(), omegas = [10], to_show_progress=False) -> None:
#         super().__init__(axis, n_measurements, to_show_progress=to_show_progress, offsets_of_axis=offsets_of_axis)
#         if motor is None:
#             motor = Gyems(bus)
#         print("motor is being connected")
#         self.connect_motor(motor, bus)
#         print("motor connected")
#         self.i_omega = 0
#         self.coeffs = []
#         self.set_omegas(omegas)
#         self.rot_dir = 1

#     def connect_motor(self, motor: Gyems, bus: CanBus):
#         self.motor = motor
#         print("motor set")
#         self.bus = bus
#         print("bus set")
#         motor.enable()
#         print("motor enabled")
#         motor.set_zero()
#         print("motor set to zero")

#     def disconnect_motor(self):
#         self.motor.disable(True)
#         self.bus.close()

#     def update_speed(self, omega):
#         self.omega = omega
#         self.motor.set_angle(self.rot_dir * 720, self.omega)
#         self.rot_dir *= -1

#     def set_omegas(self, omegas: list[float]):
#         """
#         omegas - list of motor speeds
#         """
#         self.omegas = omegas
#         self.n_omegas = len(omegas) - 1


#     # TODO: connect to motor - make the code which changes the speed of the motor
#     def update(self, xyz):
#         try:
#             result =  super().update(xyz)
#             self.coeff = self.coeff/self.omega
#             self.coeffs.append(self.coeff)
#             # check to change the motos speed or not
#             if result == 1 and self.i_omega < self.n_omegas:
#                 self.i_omega +=1
#                 self.omega = self.omegas[self.i_omega]
#                 return 0
#             return result
#         except:
#             self.disconnect_motor()
#             print("in update gyro motor disconnected")
#             # error
#             return 2


# bus = CanBus()
# motor = Gyems(bus=bus)
# calibration_gyr = Calibration_gyro(motor=motor, bus=bus, omegas=[10, 20])


async def main():
    calibr_results = {}
    worker = AsyncRedisWorker()

    calibration_acc_1 = Calibration_acc(
        n_measurements=1000, to_show_progress=True)
    async for message in worker.subscribe(count=10000):
        if calibration_acc_1.calibration_is_finished:
            break
        calibration_acc_1.calibrate(message.imu_1.acc)

    print("\n_____\nNext IMU calibration starts!")
    calibration_acc_2 = Calibration_acc(
        n_measurements=1000, to_show_progress=True)
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

    # offsets_json = json.dumps(offsets_1)
    # coefficients_json = json.dumps(coefficients_1)

    # await worker.broker.publish("imu_1_offsets_acc", offsets_json)
    # await worker.broker.publish("imu_1_coeffitients_acc", coefficients_json)
    # await worker.r.set('offsets', offsets_json)
    # await worker.r.set('coeffitients', coefficients_json)


if __name__ == '__main__':
    # try:
    asyncio.run(main())

    # except:
    #     redis_worker.r.reset()
    #     motor.disable(True)
    #     bus.close()


# except:
#     print("exception from 240 line")
# except KeyboardInterrupt:
    # serialPort.close()  # close port
    # np.savetxt("imu_results_16.csv", a, delimiter=";",
    #            header=";".join(headers))

    # df = pd.read_csv("imu_results.csv", delimiter=";")  # will be used in future work with big data
    # print(df.head())
# except:
#     serialPort.close()  # close port
#     print("Strange exception")
