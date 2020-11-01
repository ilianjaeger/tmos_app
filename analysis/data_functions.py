import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pickle
import os.path


def vicon_euclidean_distance(df1, df2=None, cols=None):
    if cols is None:
        cols = ['pos_x', 'pos_y']
    if df2 is None:
        return np.linalg.norm(df1[cols].values, axis=1)
    return np.linalg.norm(df1[cols].values - df2[cols].values, axis=1)


def euclidean_distance(vec1, vec2=None):
    if vec2 is None:
        return np.linalg.norm(vec1, axis=1)

    return np.linalg.norm(vec1 - vec2, axis=1)


def normalize_data(df1, lim=1000):
    return lim * (df1 - df1.min()) / (df1.max() - df1.min())


def compensate_temp(data, temp, ref_gradient, ref_temp=23.0):
    return data - (temp - ref_temp) * ref_gradient


def moving_average(data, n_points, remove_nan=False):
    if remove_nan:
        return data.rolling(n_points, min_periods=1).mean()

    return data.rolling(n_points).mean()


def get_data_from_file(filename, norm_time=True):
    final_data = dict()

    # TMOS
    tmos_col_names = ["col_2", "in_time", "dist_raw", "temp", "dist_raw_filt", "vel", "bin_1", "bin_2"]
    if os.path.isfile(filename + "_SENSOR_1.log"):
        final_data["tmos1"] = pd.read_csv(filename + "_SENSOR_1.log", names=tmos_col_names, index_col=0)
    if os.path.isfile(filename + "_SENSOR_2.log"):
        final_data["tmos2"] = pd.read_csv(filename + "_SENSOR_2.log", names=tmos_col_names, index_col=0)
    if os.path.isfile(filename + "_SENSOR_3.log"):
        final_data["tmos3"] = pd.read_csv(filename + "_SENSOR_3.log", names=tmos_col_names, index_col=0)
    if os.path.isfile(filename + "_SENSOR_4.log"):
        final_data["tmos4"] = pd.read_csv(filename + "_SENSOR_4.log", names=tmos_col_names, index_col=0)

    # Vicon
    vicon_col_names = ["obj", "pos_x", "pos_y", "pos_z"]
    if os.path.isfile(filename + "_VICON.log"):
        vicon_data = pd.read_csv(filename + "_VICON.log", names=vicon_col_names, index_col=0, dtype={'obj': object})

        vicon_tmos_data = vicon_data.loc[vicon_data.obj == 'TMOS']
        vicon_tmos_data = vicon_tmos_data[
            ~((vicon_tmos_data.pos_x == 0) & (vicon_tmos_data.pos_y == 0) & (vicon_tmos_data.pos_z == 0))]  # remove 0s
        vicon_tmos_pos = vicon_tmos_data.mean()

        vicon_person_data = vicon_data.loc[vicon_data.obj == 'Person']
        vicon_person_data = vicon_person_data[
            ~((vicon_person_data.pos_x == 0) & (vicon_person_data.pos_y == 0) & (
                    vicon_person_data.pos_z == 0))]

        if len(vicon_data.loc[vicon_data.obj == 'TMOS']) == 0:
            vicon_tmos_pos.pos_x = 0
            vicon_tmos_pos.pos_y = 0
            vicon_tmos_pos.pos_z = 0

        ''' GET TRUE DISTANCE '''
        final_data["vicon"] = pd.DataFrame(data=vicon_euclidean_distance(vicon_person_data, vicon_tmos_pos),
                                                  index=vicon_person_data.index, columns=['dist_true'])

    if norm_time:
        for i in final_data:
            if i in final_data:
                final_data[i].index = final_data[i].index / 1000.0

    return final_data


def merge_sensor_to_vicon(pd_sensor, pd_vicon):
    merged_data = pd.concat([pd_vicon, pd_sensor], axis=1)
    return merged_data.interpolate().ffill().bfill()  # Match data on index and fill NaNs


def crop_data_time(data, min, max):
    return data[(data.index > min) & (data.index < max)]


def get_fit_func(data_x, data_y, degree, save_func=False):
    try:
        fitted_func = np.poly1d(np.polyfit(data_x, data_y, degree))

        if save_func:
            with open("fit_func_1.pckl", 'bw') as f:
                pickle.dump(fitted_func, f)
    except np.linalg.LinAlgError:
        return None

    return fitted_func


def plot_sensor_data(data, func=None):
    fig, combined_ax = plt.subplots(4, sharex='col')
    combined_ax[0].plot(data.index, data.dist_raw, label="Sensor value 1")
    combined_ax[0].plot(data.index, data.dist_raw_filt, label="Sensor value 2")
    combined_ax[0].set_ylabel("Sensor value 1 and 2")
    combined_ax[0].grid(True)
    combined_ax[0].legend()

    combined_ax[1].plot(data.index, data.vel)
    combined_ax[1].set_ylabel("Velocity")
    combined_ax[1].grid(True)

    combined_ax[2].plot(data.index, data.bin_1, label="Sensor value 3")
    combined_ax[2].plot(data.index, data.bin_2, label="Sensor value 4")
    combined_ax[2].set_ylabel("Sensor value 3 and 4")
    combined_ax[2].grid(True)

    combined_ax[3].plot(data.index, data.temp)
    combined_ax[3].set_ylabel("Temperature")
    combined_ax[3].set_xlabel("Time [s]")
    combined_ax[3].grid(True)

    #
    # _, error_ax = plt.subplots(2, sharex='col')
    # error_ax[0].plot(data.shifted, np.log(data.dist_true), label="True log ratio")
    # if func is not None:
    #     error_ax[0].plot(data.shifted, func(data.shifted), label="Estimated log ratio")
    # error_ax[0].set_title("Log data-distance Relationship")
    # error_ax[0].set_ylabel("Log of True Distance")
    # error_ax[0].grid(True)
    # error_ax[0].legend()
    #
    # error_ax[1].plot(data.shifted, data.dist_true, label="True ratio")
    # if func is not None:
    #     error_ax[1].plot(data.shifted, np.exp(func(data.shifted)), label="Estimated ratio")
    # error_ax[1].set_title("data-distance Relationship")
    # error_ax[1].set_xlabel("Sensor Value")
    # error_ax[1].set_ylabel("True Distance")
    # error_ax[1].grid(True)
    # error_ax[1].legend()
    #
    # _, combined_ax = plt.subplots(3, sharex='col')
    # if func is not None:
    #     combined_ax[0].plot(data.index, np.exp(func(data.shifted)), label="Estimated distance")
    # combined_ax[0].plot(data.index, data.dist_true, label="True distance")
    # combined_ax[0].set_title("Sensor and Distance Data")
    # combined_ax[0].set_ylabel("Distance")
    # combined_ax[0].grid(True)
    # combined_ax[0].legend()
    #
    # combined_ax[1].plot(data.index, data.dist_raw, label="Sensor raw value")
    # combined_ax[1].plot(data.index, data.dist_filt, label="Sensor filtered value")
    # combined_ax[1].plot(data.index, data.shifted, label="Sensor filtered value (shift)")
    # combined_ax[1].set_ylabel("Sensor Data")
    # combined_ax[1].grid(True)
    # combined_ax[1].legend()
    #
    # combined_ax[2].plot(data.index, 10 * data.vel)
    # combined_ax[2].plot(data.index, np.gradient(data.dist_true, data.index))
    # combined_ax[2].set_xlabel("Time [s]")
    # combined_ax[2].set_ylabel("Sensor Velocity")
    # combined_ax[2].grid(True)
