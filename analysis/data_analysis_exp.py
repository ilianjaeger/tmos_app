import os
import sys
sys.path.extend([os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + os.sep + os.pardir)])

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from analysis import data_functions

''' MERGE ALL DATA '''
# merged_data = pd.concat([vicon_true_dist, tmos_data], axis=1)
# merged_data = merged_data.interpolate().ffill().bfill()  # Match data on index and fill NaNs

data = data_functions.get_data_from_file("../output/1_STEP_FAST")
data_functions.plot_sensor_data(data["tmos1"])

merged = data_functions.merge_sensor_to_vicon(data["tmos1"], data["vicon"])
merged = data_functions.crop_data_time(merged, 0, 100)

merged.dist_raw = data_functions.compensate_temp(merged.dist_raw, merged.temp, -1695.67645297)
merged.dist_raw = data_functions.moving_average(merged, 15, True).dist_raw
merged.dist_raw = merged.shift(-10).ffill().dist_raw

print(merged)

func = data_functions.get_fit_func(merged.dist_raw.values, np.log(merged.dist_true.values), 5)

fig, combined_ax = plt.subplots(3, sharex="col")
combined_ax[0].plot(merged.index, merged.dist_raw, label="Sensor value 1")
combined_ax[0].plot(merged.index, merged.dist_true, label="True distance")
if func is not None:
    combined_ax[0].plot(merged.index, np.exp(func(merged.dist_raw)), label="Estimated distance")
combined_ax[0].set_ylabel("Sensor and true distance")
combined_ax[0].grid(True)
combined_ax[0].legend()

combined_ax[1].plot(merged.index, merged.dist_true - np.exp(func(merged.dist_raw)), label="Difference true x estimated")
combined_ax[1].grid(True)
combined_ax[1].legend()

combined_ax[2].plot(merged.index, merged.vel, label="Velocity")
# combined_ax[2].plot(merged.index, data_functions.normalize_data(data_functions.moving_average(pd.DataFrame(data=np.gradient(merged.dist_true, merged.index), index=merged.index)[0], 8), 400), label="Velocity")
combined_ax[2].grid(True)
combined_ax[2].legend()

_, error_ax = plt.subplots(2, sharex='col')
error_ax[0].plot(merged.dist_raw, np.log(merged.dist_true), label="True log ratio")
if func is not None:
    error_ax[0].plot(merged.dist_raw, func(merged.dist_raw), label="Estimated log ratio")
error_ax[0].set_title("Log data-distance Relationship")
error_ax[0].set_ylabel("Log of True Distance")
error_ax[0].grid(True)
error_ax[0].legend()

error_ax[1].plot(merged.dist_raw, merged.dist_true, label="True ratio")
if func is not None:
    error_ax[1].plot(merged.dist_raw, np.exp(func(merged.dist_raw)), label="Estimated ratio")
error_ax[1].set_title("data-distance Relationship")
error_ax[1].set_xlabel("Sensor Value")
error_ax[1].set_ylabel("True Distance")
error_ax[1].grid(True)
error_ax[1].legend()

plt.show()

