import asyncio
import json
import numpy as np
import matplotlib.pyplot as plt
from MadgwickPlotter import MadgwickPlotter
from MadgwickFilter import MadgwickAHRS
import redis
from Filtration import IMUCoeffitientsLoader
from redis_worker import AsyncRedisWorker
from config import headers


# r = redis.Redis(host='localhost', port=6379, decode_responses=True)
# redis_worker = RedisWorker(redis_db=r, headers=headers)

mf: MadgwickAHRS = MadgwickAHRS(omega_e=100)
n_calib_frames: int = 1000

# offsets_json: str | None = redis_worker.r.get('offsets')
# coefficients_json: str | None = redis_worker.r.get('coeffitients')


# offsets = json.loads(offsets_json)

# offsets = [offsets['x'], offsets['y'], offsets['z']]
# coefficients = json.loads(coefficients_json)
# coefficients = [coefficients['x'], coefficients['y'], coefficients['z']]


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
