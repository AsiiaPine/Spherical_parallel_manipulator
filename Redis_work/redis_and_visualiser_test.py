import asyncio
import json
import numpy as np
import matplotlib.pyplot as plt
from MadgwickPlotter import MadgwickPlotter
from MadgwickFilter import MadgwickAHRS
import redis
from Spherical_parallel_manipulator.Redis_work.IMUCoefficientLoader import IMUCoeffitientsLoader
from redis_worker import AsyncRedisWorker
from config import headers


# Creates an instance of the MadwickAHRS filter
mf: MadgwickAHRS = MadgwickAHRS(omega_e=100)

madgwick_state = MadgwickPlotter(
    madg_filter=mf,
    to_draw_imu_data=True,
    to_draw_3d=False,
    window_size=20,
)


async def main():

    filename = "calib_data.json"
    coeff = IMUCoeffitientsLoader.from_file(filename)
    # Calibration parameters
    imu_2_coeffs = coeff.imu_2.coeffs_acc
    imu_2_offset = coeff.imu_2.offset_acc

    worker = AsyncRedisWorker()
    async for message in worker.subscribe(count=10000):
        # print(message)
        # Without calibration
        # mf.update_IMU(accel_data=(message.imu_2.acc), gyros_data=message.imu_2.gyro)

        # with calibration
        mf.update_IMU(accel_data=(message.imu_2.acc)/imu_2_coeffs, gyros_data=message.imu_2.gyro)

        madgwick_state.update_plot()


if __name__ == '__main__':
    asyncio.run(main())
