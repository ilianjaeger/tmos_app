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


''' GET DATA '''
# TMOS
tmos_col_names = ["col_2", "in_time", "dist_raw", "temp", "dist_filt", "vel", "bin_1", "bin_2"]
tmos_data = pd.read_csv("output/door/1_DOOR_TOP_TILT.log", names=tmos_col_names, index_col=0)
tmos_data.index = tmos_data.index / 1000
#tmos_data.dist_raw = -tmos_data.dist_raw
#tmos_data.dist_filt = -tmos_data.dist_filt

fig, combined_ax = plt.subplots(4, sharex='col')
combined_ax[0].plot(tmos_data.index, tmos_data.dist_raw, label="Sensor value 1")
combined_ax[0].plot(tmos_data.index, tmos_data.dist_filt, label="Sensor value 2")
combined_ax[0].set_ylabel("Sensor value 1 and 2")
combined_ax[0].grid(True)
combined_ax[0].legend()

combined_ax[1].plot(tmos_data.index, tmos_data.vel)
combined_ax[1].set_ylabel("Velocity")
combined_ax[1].grid(True)


combined_ax[2].plot(tmos_data.index, tmos_data.bin_1, label="Sensor value 3")
combined_ax[2].plot(tmos_data.index, tmos_data.bin_2, label="Sensor value 4")
combined_ax[2].set_ylabel("Sensor value 3 and 4")
combined_ax[2].grid(True)

combined_ax[3].plot(tmos_data.index, tmos_data.temp)
combined_ax[3].set_ylabel("Temperature")
combined_ax[3].set_xlabel("Time [s]")
combined_ax[3].grid(True)

plt.show()
