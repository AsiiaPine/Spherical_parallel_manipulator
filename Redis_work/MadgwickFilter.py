import numpy as np 
from scipy import linalg

from quaternion_calculation import *

class MadgwickAHRS:
    def __init__(self, omega_e, sample_period=1 / 256, quaternion=None, beta: np.ndarray=np.zeros(4), hpf=0):
        if quaternion is None:
            quaternion = np.array([1.0, 0.0, 0.0, 0.0], dtype=float)
        self.sample_period: float = sample_period
        self.quaternion: np.ndarray = quaternion
        self.prev_quaternion: np.ndarray = quaternion

        if beta is np.zeros(4):
            beta = np.sqrt(3)/2 * omega_e
        self.beta: np.ndarray = beta
        self.hpf: float = hpf

        self.acc = np.zeros(3)
        self.gyr = np.zeros(3)

    # def calibrate():

    def update_IMU(self, gyros_data: np.ndarray, accel_data: np.ndarray):
        self.acc = accel_data
        self.gyr = gyros_data
        q: np.ndarray = self.quaternion
        # q_prev: np.ndarray = self.prev_quaternion
        # alpha = self.hpf
        # Normalise accelerometer measurement
        assert accel_data is not None
        assert gyros_data is not None

        accel_data = accel_data/np.linalg.norm(accel_data)
        # Gradient decent algorithm corrective step
        F: np.ndarray = np.array([2 * (q[1] * q[3] - q[0] * q[2]) - accel_data[0],
                                  2 * (q[0] * q[1] + q[2] * q[3]) - accel_data[1],
                                  2 * (0.5 - q[1] ** 2 - q[2] ** 2) - accel_data[2]])


        J: np.ndarray = np.array([[
            -2 * q[2], 2 * q[3], -2 * q[0], 2 * q[1]],
            [2 * q[1], 2 * q[0], 2 * q[3], 2 * q[2]],
            [0, -4 * q[1], -4 * q[2], 0]])

        tolerance = 0.01
        step: np.ndarray = (J.T @ F) #.flatten()
        # step: np.ndarray = - normalize(step, tolerance=tolerance)  # normalise step magnitude
        if np.linalg.norm(step) < 0.001:
            return
        step: np.ndarray = - step/np.linalg.norm(step)  # normalise step magnitude

        # Compute rate of change of quaternion
        qDot_omega = get_q_dot(q, gyros_data)
        self.qDot_omega = qDot_omega
        qDot: np.ndarray = qDot_omega + self.beta * step
        
        self.qDot = qDot
        # Integrate to yield quaternion
        q = quaternion_exponential_integration(q = q, omega_=qDot, dt=self.sample_period)
        norm = np.linalg.norm(q)
        if norm > 0.8 and norm < 1.2:
            self.quaternion = q/norm



        # qDot: np.ndarray = 0.5 * multiply_quaternions(q, np.array(
        #     [0, gyros_data[0], gyros_data[1], gyros_data[2]])) - self.beta * step

        # q += qDot * self.sample_period
        # get_norm = lambda x: np.sqrt(x[1] ** 2 + x[2] ** 2 + x[3] ** 2)

        # q[1:] = q[1:]/get_norm(q)
        # q = normalize(q, tolerance)
        # self.quaternion: np.ndarray = np.hstack([q[0], q[1:] / np.linalg.norm(q[1:])])  # normalise quaternion

        # assert np.linalg.norm(q[1:]) <= 1 + 2 * tolerance

    #
        # # Compute rate of change of quaternion
        # qDot_omega = get_q_dot(q, gyros_data)
        # qDot: np.ndarray = qDot_omega - self.beta * step
        # # Integrate to yield quaternion
        # q += qDot * self.sample_period
        # # q = self.hpf * q + self.hpf * (0.5 * quaternProd(q, [0 Gyroscope[1] Gyroscope[2] Gyroscope[3]]) - self.Beta * step') * self.SamplePeriod;
        # get_norm = lambda x: np.sqrt(x[0] ** 2 + x[1] ** 2 + x[2] ** 2 + x[3] ** 2)
        #
        # q = q / get_norm(q)
        # # q = normalize(q, tolerance)
        # self.quaternion = q
        # # self.quaternion: np.ndarray = np.hstack([q[0], q[1:] / np.linalg.norm(q[1:])])  # normalise quaternion
        #
        # assert np.linalg.norm(q) <= 1 + 2 * tolerance


    # def update_IMU(self, gyros_data: np.ndarray, accel_data: np.ndarray):
    #     q: np.ndarray = self.quaternion
    #     # q_prev: np.ndarray = self.prev_quaternion
    #     # alpha = self.hpf
    #     # Normalise accelerometer measurement
    #     if np.linalg.norm(accel_data) == 0:
    #         return  # handle NaN
    #     accel_data  = accel_data / np.linalg.norm(accel_data)  # normalise magnitude
    #
    #     # Gradient decent algorithm corrective step
    #     F: np.ndarray = np.array([2 * (q[1] * q[3] - q[0] * q[2]) - accel_data[0],
    #                   2 * (q[0] * q[1] + q[2] * q[3]) - accel_data[1],
    #                   2 * (0.5 - q[1] ** 2 - q[2] ** 2) - accel_data[2]])
    #     J: np.ndarray = np.array([[-2 * q[2], 2 * q[3], -2 * q[0], 2 * q[1]],
    #                   [2 * q[1], 2 * q[0], 2 * q[3], 2 * q[2]],
    #                   [0, -4 * q[1], -4 * q[2], 0]])
    #
    #     step: np.ndarray = (J.T @ F).flatten()
    #     step: np.ndarray = step / np.linalg.norm(step)  # normalise step magnitude
    #
    #     # Compute rate of change of quaternion
    #     qDot: np.ndarray = 0.5 * multiply_quaternions(q, np.array([0, gyros_data[0], gyros_data[1], gyros_data[2]])) - self.beta * step
    #     # Integrate to yield quaternion
    #     q += qDot * self.sample_period
    #     # q = self.hpf * q + self.hpf * (0.5 * quaternProd(q, [0 Gyroscope[1] Gyroscope[2] Gyroscope[3]]) - self.Beta * step') * self.SamplePeriod;
    #
    #     self.quaternion: np.ndarray = q / np.linalg.norm(q)  # normalise quaternion
    #

    # def update(self, gyros_data, accel_data, magne_data):
    #     q = self.quaternion
    #     # Normalise accelerometer measurement
    #     if np.linalg.norm(accel_data) == 0:
    #         return
    #     accelerometer = accel_data / np.linalg.norm(accel_data)

    #     # Normalise magnetometer measurement
    #     if np.linalg.norm(magne_data) == 0:
    #         return
    #     magnetometer = magne_data / np.linalg.norm(magne_data)

    #     # Reference direction of Earth's magnetic field
    #     h: np.ndarray = multiply_quaternions(q, multiply_quaternions([0, magnetometer], quaternion_conj(q)))
    #     b: np.ndarray = np.array([0, np.linalg.norm([h[1], h[2]]), 0, h[3]])

    #     # Gradient descent algorithm corrective step
    #     F = [2 * (q[1] * q[3] - q[0] * q[2]) - accelerometer[0],
    #          2 * (q[0] * q[1] + q[2] * q[3]) - accelerometer[1],
    #          2 * (0.5 - q[1] ** 2 - q[2] ** 2) - accelerometer[2],
    #          2 * b[1] * (0.5 - q[2] ** 2 - q[3] ** 2) + 2 * b[3] * (q[1] * q[3] - q[0] * q[2]) - magnetometer[0],
    #          2 * b[1] * (q[1] * q[2] - q[0] * q[3]) + 2 * b[3] * (q[0] * q[1] + q[2] * q[3]) - magnetometer[1],
    #          2 * b[1] * (q[0] * q[2] + q[1] * q[3]) + 2 * b[3] * (0.5 - q[1] ** 2 - q[2] ** 2) - magnetometer[2]]
    #     J = np.array([[-2 * q[2], 2 * q[3], -2 * q[0], 2 * q[1]],
    #                   [2 * q[1], 2 * q[0], 2 * q[3], 2 * q[2]],
    #                   [0, -4 * q[1], -4 * q[2], 0],
    #                   [-2 * b[3] * q[1], 2 * b[3] * q[2], -4 * b[1] * q[1] - 2 * b[3] * q[0],
    #                    -4 * b[1] * q[2] + 2 * b[3] * q[3]],
    #                   [-2 * b[1] * q[3] + 2 * b[3] * q[1], 2 * b[1] * q[2] + 2 * b[3] * q[0],
    #                    2 * b[1] * q[1] + 2 * b[3] * q[3], -2 * b[1] * q[0] + 2 * b[3] * q[2]],
    #                   [2 * b[1] * q[2], 2 * b[1] * q[3] - 4 * b[3] * q[1], 2 * b[1] * q[0] - 4 * b[3] * q[2],
    #                    2 * b[1] * q[1]]])
    #     step = np.dot(J.T, F)
    #     step = step / np.linalg.norm(step)

    #     # Compute rate of change of quaternion
    #     qDot = 0.5 * multiply_quaternions(q, [0, gyros_data[0], gyros_data[1], gyros_data[2]]) - self.beta * step

    #     # Integrate to yield quaternion
    #     q = q + qDot * self.sample_period
    #     self.quaternion = q / np.linalg.norm(q)
