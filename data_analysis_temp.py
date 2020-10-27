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


def exp_fit(x, a, b, c):
    return a * np.exp(0.0005 * b * x) + c


def lin_fit(x, a, b):
    return a * x + b


''' GET DATA '''
# TMOS
tmos_col_names = ["col_2", "in_time", "dist_raw", "temp", "dist_filt", "vel", "bin_1", "bin_2"]
tmos_data = pd.read_csv("output/1_TEMP_3_SENSOR_1.log", names=tmos_col_names, index_col=0)
tmos_data.index = tmos_data.index / 1000
tmos_data.dist_raw = -tmos_data.dist_raw
tmos_data.dist_filt = -tmos_data.dist_filt

''' LINEAR TEMP FIT '''
popt, _ = curve_fit(lin_fit, tmos_data.temp, tmos_data.dist_raw)
print(popt)

''' PLOTS '''
fig, axes = plt.subplots(2, 1, sharex='col')
fig.suptitle("Sensor raw data")
axes[0].plot(tmos_data.index, tmos_data.dist_raw, label="TMOS dist raw")
axes[0].plot(tmos_data.index, tmos_data.dist_filt, label="TMOS dist filtered")
axes[0].set_title("TMOS raw/comp data")
axes[0].grid(True)
axes[0].legend()

axes[1].plot(tmos_data.index, tmos_data.temp, label="Temperature")
axes[1].set_title("Temperature")
axes[1].grid(True)
axes[1].legend()

fig2 = plt.figure("Temperature Dependence")
ax = fig2.add_subplot(111)
ax.plot(tmos_data.temp, tmos_data.dist_raw, label="Sensor data [TMOS 2]")
ax.plot(tmos_data.temp, lin_fit(tmos_data.temp, popt[0], popt[1]), label="Linear fit")
ax.set_title("Temperature Dependence")
ax.set_xlabel("Temperature")
ax.set_ylabel("Sensor reading")
ax.grid(True)
ax.legend()


plt.show()

