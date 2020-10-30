import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


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
tmos_data = pd.read_csv("../output/door/1_DOOR_TILT_EXTREME.log", names=tmos_col_names, index_col=0)

# Get time value in seconds
tmos_data.index = tmos_data.index / 1000

# Temperature compansation
tmos_data.dist_raw = compensate_temp(tmos_data.dist_raw, tmos_data.temp, 23.0, -1426.57019003)

# Moving average
tmos_data["dist_mov"] = tmos_data.dist_raw.rolling(8).mean()  # min_periods=1

# Set origin and remove point below this threshold
origin = tmos_data[tmos_data.index < 5.0].dist_mov.mean()
tmos_data.dist_mov = tmos_data.dist_mov - origin
tmos_data.dist_mov[tmos_data.dist_mov < 0.0] = 0
print("Origin:", origin)

print(tmos_data.info())

mov_thresh = 500
mov_detected = False
door_movement_array = []
door_movement_detect_time = []
door_movement_detect_pos = []
door_movement_detect_type = []
for index, data_point in tmos_data.iterrows():
    if data_point.dist_mov > mov_thresh:
        mov_detected = True

        door_movement_array.append(data_point.dist_mov)
    else:
        if mov_detected and len(door_movement_array) != 0:
            # Detect type
            index_of_max = door_movement_array.index(max(door_movement_array))

            if index_of_max > len(door_movement_array) / 2:
                door_movement_detect_type.append("in")
            else:
                door_movement_detect_type.append("out")

            door_movement_array = []
            door_movement_detect_time.append(index)
            door_movement_detect_pos.append(data_point.dist_mov)
            mov_detected = False

print(door_movement_detect_time)

fig, combined_ax = plt.subplots(4, sharex='col')
combined_ax[0].plot(tmos_data.index, tmos_data.dist_raw, label="Sensor value 1")
combined_ax[0].plot(tmos_data.index, tmos_data.dist_filt, label="Sensor value 2")
combined_ax[0].plot(tmos_data.index, tmos_data.dist_mov, label="Moving average")
combined_ax[0].plot(door_movement_detect_time, door_movement_detect_pos, 'X', label="Door movement")

for ind, val in enumerate(door_movement_detect_type):
    combined_ax[0].annotate(val, (door_movement_detect_time[ind], door_movement_detect_pos[ind]))

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
