from MadgwickFilter import MadgwickAHRS
from drawing import draw_rotation
from drawing import plot_imu_data


import matplotlib.pyplot as plt
import numpy as np


import time
import warnings


class MadgwickPlotter:
    def __init__(
        self,
            madg_filter: MadgwickAHRS,
            n_calib_frames: int = 100,
            t_start: float = time.time(),
            to_draw_3d: bool = False,
            to_draw_imu_data: bool = False,
            window_size: int = 20,
            imu_n: int = 0,
            offsets_acc=[0, 0, 0],
            coeffs_acc=[1, 1, 1],
    ) -> None:
        self.gyr_array = np.zeros((2, 3))
        self.acc_array = np.zeros((2, 3))

        self.offsets_acc = offsets_acc
        self.coeffs_acc = coeffs_acc

        self.time_window = [0.0, 0.0]

        self.madgwick = madg_filter

        self.window_size = window_size
        self.start_time = t_start
        self.prev_time = t_start

        self.to_draw_3d = to_draw_3d
        self.to_draw_imu_data = to_draw_imu_data

        if to_draw_3d and to_draw_imu_data:
            warnings.warn(
                "Warning...........Dude, choose what to draw, not two in a time (((")
            to_draw_3d = False
            to_draw_imu_data = False

        if to_draw_3d:
            self.theta = 0
            self.fig = plt.figure()
            self.ax = self.fig.add_subplot(projection='3d')
            self.ax.axis('off')

        if to_draw_imu_data:
            self.i = 0
            self.imu_n = imu_n
            self.imu_axs, self.imu_fig = plot_imu_data(
                np.zeros((3, 3)), np.zeros((3, 3)), imu=imu_n, time=np.zeros(3)*t_start)

    def get_Madgwick_data(self):
        if self.to_draw_imu_data:
            self.acc = self.madgwick.acc
            self.gyr = self.madgwick.gyr
        else:
            self.madgwick.quaternion

    def plot_3d_view(self):
        self.ax.clear()
        _, self.theta, _, _, _,  _, _ = draw_rotation(
            quaternion=self.madgwick.quaternion, t=self.curr_time, fig=self.fig, ax=self.ax, theta=self.theta)
        # plt.pause(0.5)
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.pause(0.0001)


    def plot_2d_data(self):
        for ax in self.imu_axs:
            ax.clear()
        if self.i > self.window_size:
            self.time_window = self.time_window[1:]
            self.acc_array = self.acc_array[1:]
            self.gyr_array = self.gyr_array[1:]
        self.acc_array = np.vstack((self.acc_array, self.acc))
        self.gyr_array = np.vstack((self.gyr_array, self.gyr))
        self.i +=1
        plot_imu_data(self.acc_array, self.gyr_array, imu=self.imu_n,
                        fig=self.imu_fig, axs=self.imu_axs, time=self.time_window)
        plt.pause(0.0001)


    def update_plot(self):
        self.curr_time = time.time() - self.start_time
        self.time_window.append(self.curr_time)
        self.get_Madgwick_data()
        if self.to_draw_3d:
            self.plot_3d_view()
        else:
            self.plot_2d_data()
           
            
    # def set_Madgwick_data(self, acc, gyro):

    #     assert type(self.prev_time) is float
    #     curr_time = time.time() - self.start_time
    #     dt = curr_time - self.prev_time
    #     self.time_window.append(curr_time)
    #     assert type(self.acc_array) is np.ndarray
    #     assert type(self.gyr_array) is np.ndarray

    #     assert type(self.madgwick) is MadgwickAHRS

    #     if np.linalg.norm(acc):
    #         acc = acc/np.linalg.norm(acc)

    #     self.acc_array = np.vstack((self.acc_array, acc))
    #     self.gyr_array = np.vstack((self.gyr_array, gyro))

    #     if self.i > self.window_size:
    #         self.time_window = self.time_window[1:]
    #         self.acc_array = self.acc_array[1:]
    #         self.gyr_array = self.gyr_array[1:]

    #     if self.to_draw_3d:
    #         self.madgwick.sample_period = dt
    #         self.madgwick.update_IMU(
    #             gyros_data=self.gyr_array[-1], accel_data=self.acc_array[-1])

    #         self.ax.clear()
    #         _, self.theta, _, _, _,  _, _ = draw_rotation(
    #             quaternion=self.madgwick.quaternion, t=curr_time, fig=self.fig, ax=self.ax, theta=self.theta)
    #         # plt.pause(0.5)
    #         self.fig.canvas.draw()
    #         self.fig.canvas.flush_events()
    #         plt.pause(0.0001)

    #     if self.to_draw_imu_data:
    #         for ax in self.imu_axs:
    #             ax.clear()
    #         plot_imu_data(self.acc_array, self.gyr_array, imu=self.imu_n,
    #                       fig=self.imu_fig, axs=self.imu_axs, time=self.time_window)
    #         self.imu_fig.canvas.draw()
    #         self.imu_fig.canvas.flush_events()

    #         # print(self.to_draw)
    #     self.i += 1
    #     self.prev_time = curr_time

    # def update_state(self, acc, gyro):
        # print("i", self.i)

        # if self.i < self.n_calib_frames:
        #     self.collect_data(acc, gyro)

        # if self.i == self.n_calib_frames:
        #     self.set_Madgwick_parameters(acc, gyro)
        #     print("Parameters updated:", self.omega_beta, self.epsilon_beta)

        # if self.i > self.n_calib_frames:
        #     self.set_Madgwick_data(acc, gyro)
        # self.i += 1

    # def update(self, acc, gyro):
    #     self.n_calib_frames = 0
    #     acc_norm = np.array(
    #         [(acc[i]-self.offsets_acc[i])/self.coeffs_acc[i] for i in range(3)])
    #     self.set_Madgwick_data(acc=acc_norm, gyro=gyro)
