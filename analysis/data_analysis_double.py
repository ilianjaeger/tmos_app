import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from scipy.optimize import curve_fit


def euclidean_distance(df1, df2=None, cols=None):
    if cols is None:
        cols = ['pos_x', 'pos_y']
    if df2 is None:
        return np.linalg.norm(df1[cols].values, axis=1)
    return np.linalg.norm(df1[cols].values - df2[cols].values, axis=1)


def normalize_data(df1, lim=1000):
    return lim * (df1 - df1.min()) / (df1.max() - df1.min())


def compensate_temp(data, temp, ref_temp, ref_gradient):
    return data - (temp - ref_temp) * ref_gradient


''' GET DATA '''
# TMOS
tmos_col_names = ["col_2", "in_time", "dist_raw", "temp", "dist_filt", "vel", "bin_1", "bin_2"]
tmos_data_1 = pd.read_csv("output/TEST_3_SENSOR_1.log", names=tmos_col_names, index_col=0)
tmos_data_2 = pd.read_csv("output/TEST_3_3_SENSOR_1.log", names=tmos_col_names, index_col=0)
tmos_data = [tmos_data_1, tmos_data_2]
tmos_data[0].index = tmos_data[0].index / 1000
tmos_data[1].index = tmos_data[1].index / 1000

tmos_data[0].dist_raw = compensate_temp(tmos_data[0].dist_raw, tmos_data[0].temp, 23.0, -1426.57019003)
tmos_data[1].dist_raw = compensate_temp(tmos_data[1].dist_raw, tmos_data[1].temp, 23.0, -1426.57019003)

fig, combined_ax = plt.subplots(4, sharex='col')
combined_ax[0].plot(tmos_data[0].index, tmos_data[0].dist_raw, label="TMOS 1")
combined_ax[0].plot(tmos_data[1].index, tmos_data[1].dist_raw, label="TMOS 2")
combined_ax[0].grid(True)
combined_ax[0].legend()

combined_ax[1].plot(tmos_data[0].index, tmos_data[0].dist_filt, label="TMOS 1")
combined_ax[1].plot(tmos_data[1].index, tmos_data[1].dist_filt, label="TMOS 2")
combined_ax[1].grid(True)
combined_ax[1].legend()

combined_ax[2].plot(tmos_data[0].index, tmos_data[0].temp, label="TMOS 1")
combined_ax[2].plot(tmos_data[1].index, tmos_data[1].temp, label="TMOS 2")
combined_ax[2].grid(True)
combined_ax[2].legend()

combined_ax[3].plot(tmos_data[0].index, tmos_data[0].vel, label="TMOS 1")
combined_ax[3].plot(tmos_data[1].index, tmos_data[1].vel, label="TMOS 2")
combined_ax[3].grid(True)
combined_ax[3].legend()

plt.show()
