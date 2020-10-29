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


def get_sensor_data(filename):
    if filename is None:
        return None

    data_col_names = ["col_2", "in_time", "dist_raw", "temp", "dist_filt", "vel", "bin_1", "bin_2"]
    data = pd.read_csv(filename, names=data_col_names, index_col=0)
    data.index = data.index / 1000
    # data.dist_raw = -data.dist_raw
    # data.dist_filt = -data.dist_filt

    # data["shifted"] = data.shift(periods=-75).dist_filt
    return data


def crop_data_time(data, min, max):
    return data[(data.index > min) & (data.index < max)]


def exp_fit(x, a, b, c):
    return a * np.exp(0.0005 * b * x) + c


def lin_fit(x, a, b):
    return a * x + b


''' GET DATA '''
tmos_data_sensor_1 = get_sensor_data("output/1_TEMP_3_SENSOR_1.log")
tmos_data_sensor_2 = get_sensor_data("output/2_TEMP_3_SENSOR_1.log")

''' LINEAR TEMP FIT '''
popt, _ = curve_fit(lin_fit, tmos_data_sensor_1.temp, tmos_data_sensor_1.dist_raw)
print(popt)

''' PLOTS '''
fig, axes = plt.subplots(2, 1, sharex='col')
fig.suptitle("Sensor raw data")
axes[0].plot(tmos_data_sensor_1.index, tmos_data_sensor_1.dist_raw, label="Sensor value 1")
axes[0].plot(tmos_data_sensor_1.index, tmos_data_sensor_1.dist_filt, label="Sensor value 2")
axes[0].set_ylabel("Sensor raw data")
axes[0].grid(True)
axes[0].legend()

axes[1].plot(tmos_data_sensor_1.index, tmos_data_sensor_1.temp)
axes[1].set_xlabel("Time [s]")
axes[1].set_ylabel("Temperature")
axes[1].grid(True)

fig2 = plt.figure("Temperature Dependence")
ax1 = fig2.add_subplot(111)
ax1.plot(tmos_data_sensor_1.temp, tmos_data_sensor_1.dist_raw, label="Sensor data [TMOS 1]")
ax1.plot(tmos_data_sensor_1.temp, lin_fit(tmos_data_sensor_1.temp, popt[0], popt[1]), label="Linear fit")
ax1.set_title("Temperature Dependence")
ax1.set_xlabel("Temperature")
ax1.set_ylabel("Sensor reading")
ax1.grid(True)
ax1.legend()

fig3 = plt.figure("Sensor comparison")
ax2 = fig3.add_subplot(111)
ax2.plot(tmos_data_sensor_1.temp, tmos_data_sensor_1.dist_raw, label="Sensor data [TMOS 1]")
ax2.plot(tmos_data_sensor_2.temp, tmos_data_sensor_2.dist_raw, label="Sensor data [TNOS 2]")
ax2.set_title("Sensor comparison")
ax2.set_xlabel("Temperature")
ax2.set_ylabel("Sensor reading")
ax2.grid(True)
ax2.legend()


plt.show()

