import asyncio
from MadgwickPlotter import MadgwickPlotter
from MadgwickFilter import MadgwickAHRS
from Redis_work.IMUCoeffitientsLoader import IMUCoeffitientsLoader
from Redis_work.RedisWorker import AsyncRedisWorker


mf: MadgwickAHRS = MadgwickAHRS(omega_e=100)
n_calib_frames: int = 1000

madgwick_state = MadgwickPlotter(
    madg_filter=mf,
    n_calib_frames=n_calib_frames,
    to_draw_imu_data=True,
    to_draw_3d=False,
    window_size=20,
)


async def main():

    filename = "calib_data.json"
    coeff = IMUCoeffitientsLoader.from_file(filename)
    imu_1_coeffs = coeff.imu_1.coeffs_acc
    imu_1_offset = coeff.imu_1.offset_acc

    worker = AsyncRedisWorker()
    async for message in worker.subscribe(count=10000):
        # print(message)
        mf.update_IMU(accel_data=(message.imu_1.acc)/imu_1_coeffs, gyros_data=message.imu_1.gyro)
        madgwick_state.update_plot()


if __name__ == '__main__':
    asyncio.run(main())
