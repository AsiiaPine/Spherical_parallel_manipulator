import numpy as np
import json
from typing import TextIO
from models import IMUAccCalibrationData
from config import acc_coeffitients_str, acc_offsets_str
from dataclasses import dataclass


@dataclass
class IMUCoeffitientsLoader:
    imu_1: IMUAccCalibrationData
    imu_2: IMUAccCalibrationData

    @classmethod
    def from_file(cls, calib_data_file_name: str) -> "IMUCoeffitientsLoader":
        f = open(calib_data_file_name,)
        calib_data_s: str = json.load(f)
        f.close()
        calib_data: dict = json.loads(calib_data_s)
        imu_1 = IMUAccCalibrationData(offset_acc=calib_data["imu_1"][acc_offsets_str],
                                      coeffs_acc=calib_data["imu_1"][acc_coeffitients_str])
        imu_2 = IMUAccCalibrationData(offset_acc=calib_data["imu_2"][acc_offsets_str],
                                      coeffs_acc=calib_data["imu_2"][acc_coeffitients_str])
        return cls(imu_1=imu_1, imu_2=imu_2)

