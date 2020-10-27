import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pickle


def euclidean_distance(df1, df2=None, cols=None):
    if cols is None:
        cols = ['pos_x', 'pos_y']
    if df2 is None:
        return np.linalg.norm(df1[cols].values, axis=1)
    return np.linalg.norm(df1[cols].values - df2[cols].values, axis=1)


def normalize_data(df1, lim=1000):
    return lim * (df1 - df1.min()) / (df1.max() - df1.min())


def get_sensor_and_vicon_data(f_sensor, f_vicon):
    # TMOS
    tmos_col_names = ["col_2", "in_time", "dist_raw", "temp", "dist_filt", "vel", "bin_1", "bin_2"]
    tmos_data = pd.read_csv(f_sensor, names=tmos_col_names, index_col=0)
    tmos_data.index = tmos_data.index / 1000
    tmos_data.dist_raw = -tmos_data.dist_raw
    tmos_data.dist_filt = -tmos_data.dist_filt

    # Vicon
    vicon_col_names = ["obj", "pos_x", "pos_y", "pos_z"]
    vicon_data = pd.read_csv(f_vicon, names=vicon_col_names, index_col=0, dtype={'obj': object})
    vicon_data.index = vicon_data.index / 1000

    ''' PROCESS VICON DATA '''
    vicon_tmos_data = vicon_data.loc[vicon_data.obj == 'TMOS']
    vicon_tmos_data = vicon_tmos_data[
        ~((vicon_tmos_data.pos_x == 0) & (vicon_tmos_data.pos_y == 0) & (vicon_tmos_data.pos_z == 0))]  # remove 0s
    vicon_tmos_pos = vicon_tmos_data.mean()

    vicon_person_data = vicon_data.loc[vicon_data.obj == 'Person']
    vicon_person_data = vicon_person_data[
        ~((vicon_person_data.pos_x == 0) & (vicon_person_data.pos_y == 0) & (
                vicon_person_data.pos_z == 0))]  # Remove 0s

    if len(vicon_data.loc[vicon_data.obj == 'TMOS']) == 0:
        vicon_tmos_pos.pos_x = 0
        vicon_tmos_pos.pos_y = 0
        vicon_tmos_pos.pos_z = 0

    ''' GET TRUE DISTANCE '''
    vicon_true_dist = pd.DataFrame(data=euclidean_distance(vicon_person_data, vicon_tmos_pos),
                                   index=vicon_person_data.index, columns=['dist_true'])

    ''' MERGE ALL DATA '''
    merged_data = pd.concat([vicon_true_dist, tmos_data], axis=1)
    merged_data = merged_data.interpolate().ffill().bfill()  # Match data on index and fill NaNs

    merged_data["shifted"] = merged_data.shift(periods=-75).dist_filt

    return merged_data


def crop_data_time(data, min, max):
    return data[(data.index > min) & (data.index < max)]


def get_fit_func(data, degree, min=0.0, max=100.0, save_func=False):
    fit_data = crop_data_time(data, min, max)

    try:
        fitted_func = np.poly1d(np.polyfit(fit_data.shifted, np.log(fit_data.dist_true), degree))

        if save_func:
            with open("fit_func_1.pckl", 'bw') as f:
                pickle.dump(fitted_func, f)
    except np.linalg.LinAlgError:
        return None

    return fitted_func


def plot_general_data(data, func=None):
    _, error_ax = plt.subplots(2, sharex='col')
    error_ax[0].plot(data.shifted, np.log(data.dist_true), label="True log ratio")
    if func is not None:
        error_ax[0].plot(data.shifted, func(data.shifted), label="Estimated log ratio")
    error_ax[0].set_title("Log data-distance Relationship")
    error_ax[0].set_ylabel("Log of True Distance")
    error_ax[0].grid(True)
    error_ax[0].legend()

    error_ax[1].plot(data.shifted, data.dist_true, label="True ratio")
    if func is not None:
        error_ax[1].plot(data.shifted, np.exp(func(data.shifted)), label="Estimated ratio")
    error_ax[1].set_title("data-distance Relationship")
    error_ax[1].set_xlabel("Sensor Value")
    error_ax[1].set_ylabel("True Distance")
    error_ax[1].grid(True)
    error_ax[1].legend()

    _, combined_ax = plt.subplots(3, sharex='col')
    if func is not None:
        combined_ax[0].plot(data.index, np.exp(func(data.shifted)), label="Estimated distance")
    combined_ax[0].plot(data.index, data.dist_true, label="True distance")
    combined_ax[0].set_title("Sensor and Distance Data")
    combined_ax[0].set_ylabel("Distance")
    combined_ax[0].grid(True)
    combined_ax[0].legend()

    combined_ax[1].plot(data.index, data.dist_raw, label="Sensor raw value")
    combined_ax[1].plot(data.index, data.dist_filt, label="Sensor filtered value")
    combined_ax[1].plot(data.index, data.shifted, label="Sensor filtered value (shift)")
    combined_ax[1].set_ylabel("Sensor Data")
    combined_ax[1].grid(True)
    combined_ax[1].legend()

    combined_ax[2].plot(data.index, 10 * data.vel)
    combined_ax[2].plot(data.index, np.gradient(data.dist_true, data.index))
    combined_ax[2].set_xlabel("Time [s]")
    combined_ax[2].set_ylabel("Sensor Velocity")
    combined_ax[2].grid(True)


sensor_data_to_fit = get_sensor_and_vicon_data("output/2_LINEAR_SENSOR_1.log", "output/2_LINEAR_VICON.log")
sensor_data_to_compare = get_sensor_and_vicon_data("output/2_EVERYTHING_SENSOR_1.log", "output/2_EVERYTHING_VICON.log")

fitting_function = get_fit_func(sensor_data_to_fit, 5, 7, 16, False)  # 22.5, 41 (EVERYTHING)

plot_general_data(sensor_data_to_fit, fitting_function)
plot_general_data(sensor_data_to_compare)

plt.show()

# sensor_1_data_2 = sensor_1_data_2[((sensor_1_data_2.index > 22.5) & (sensor_1_data_2.index < 41)) | ((sensor_1_data_2.index > 50) & (sensor_1_data_2.index < 54.7)) | ((sensor_1_data_2.index > 60) & (sensor_1_data_2.index < 62.3))]
