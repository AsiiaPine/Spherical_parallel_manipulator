from dataclasses import dataclass
import numpy as np


@dataclass
class IMUData:
    acc: np.ndarray
    gyro: np.ndarray


@dataclass
class IMUMessage:
    imu_1: IMUData
    imu_2: IMUData

    @classmethod
    def from_json(cls, data: dict[str, str]):
        """
        Deserialize message from JSON received from redis.
        """

        # TODO: fix this after ESP firmware is fixed.
        # Order is currently messed up.

        imu_1 = IMUData(
            acc=np.array([
                float(data["imu_1_accel z"]),
                float(data["imu_1_accel y"]),
                float(data["imu_1_accel x"]),
            ]),
            gyro=np.array([
                float(data["imu_1_gyro z"]),
                float(data["imu_1_gyro y"]),
                float(data["imu_1_gyro x"]),
            ]),
        )
        imu_2 = IMUData(
            acc=np.array([
                float(data["imu_2_accel z"]),
                float(data["imu_2_accel y"]),
                float(data["imu_2_accel x"]),
            ]),
            gyro=np.array([
                float(data["imu_2_gyro z"]),
                float(data["imu_2_gyro y"]),
                float(data["imu_2_gyro x"]),
            ]),
        )
        return cls(imu_1=imu_1, imu_2=imu_2)


@dataclass
class IMUAccCalibrationData:
    offset_acc: np.ndarray
    coeffs_acc:np.ndarray

    # offset_gyr: np.ndarray
    # coeffs_gyr: np.ndarray

@dataclass
class IMUCalibrationMessage:
    imu_1 : IMUAccCalibrationData
    imu_2 : IMUAccCalibrationData

    # @classmethod
    # def acc_from_json(cls, data: dict[str, str]):
    #     """
    #     Deserialize message from JSON received from redis.
    #     """

    #     imu_1 = IMUCalibrationData(
    #         offset_acc=np.array([
    #             float(data["imu_1_accel z"]),
    #             float(data["imu_1_accel y"]),
    #             float(data["imu_1_accel x"]),
    #         ]),
    #         offset_gyr=np.array([["imu_1_offsets_acc"],]),
    #         coeffs_acc=np.array([
    #             float(data["imu_1_gyro z"]),
    #             float(data["imu_1_gyro y"]),
    #             float(data["imu_1_gyro x"]),
    #         ]),
    #         coeffs_gyro = np.array([
    #             [],
    #         ]),
    #     )
