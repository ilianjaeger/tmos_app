import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from scipy.optimize import curve_fit


def euclidean_distance(df1, df2, cols=None):
    if cols is None:
        cols = ['pos_x', 'pos_y']
    return np.linalg.norm(df1[cols].values - df2[cols].values, axis=1)


def normalize_data(df1, lim=1000):
    return lim * (df1 - df1.min()) / (df1.max() - df1.min())


''' GET DATA '''
# TMOS
tmos_col_names = ["col_2", "in_time", "dist_raw", "temp", "dist_filt", "vel", "bin_1", "bin_2"]
tmos_data = pd.read_csv("output/2_Sensor_fast.log", names=tmos_col_names, index_col=0)
tmos_data.index = tmos_data.index / 1000
tmos_data.dist_raw = -tmos_data.dist_raw
tmos_data.dist_filt = -tmos_data.dist_filt
tmos_data.dist_raw = np.append([0, 0, 0, 0], pd.Series(tmos_data.dist_raw).rolling(window=5).mean().iloc[5 - 1:].values)

# Vicon
vicon_col_names = ["obj", "pos_x", "pos_y", "pos_z"]
vicon_data = pd.read_csv("output/2_Vicon_fast.log", names=vicon_col_names, index_col=0,
                         dtype={'obj': object})
vicon_data.index = vicon_data.index / 1000

''' PROCESS VICON DATA '''
# Vicon data
vicon_tmos_data = vicon_data.loc[vicon_data.obj == 'TMOS']
vicon_tmos_data = vicon_tmos_data[
    ~((vicon_tmos_data.pos_x == 0) & (vicon_tmos_data.pos_y == 0) & (vicon_tmos_data.pos_z == 0))]  # remove 0s
vicon_tmos_pos = vicon_tmos_data.mean()

vicon_person_data = vicon_data.loc[vicon_data.obj == 'Person']
vicon_person_data = vicon_person_data[
    ~((vicon_person_data.pos_x == 0) & (vicon_person_data.pos_y == 0) & (vicon_person_data.pos_z == 0))]  # Remove 0s

''' GET TRUE DISTANCE '''
vicon_true_dist = pd.DataFrame(data=euclidean_distance(vicon_person_data, vicon_tmos_pos),
                               index=vicon_person_data.index, columns=['true_dist'])

''' MERGE ALL DATA '''
merged_data = pd.concat([vicon_true_dist, tmos_data], axis=1)
merged_data = merged_data.interpolate().ffill().bfill()  # Match data on index and fill NaNs

''' GET TRUE VELOCITY ESTIMATE '''
derivative = np.gradient(merged_data.true_dist, merged_data.index)

''' PLOT RAW '''
'''# TMOS data
tmos_fig = plt.figure("TMOS raw data")
tmos_ax = tmos_fig.add_subplot(111)
tmos_ax.plot(merged_data.index, merged_data.dist_raw)
tmos_ax.plot(merged_data.index, merged_data.dist_filt)

# Person trajecotry
vicon_fig = plt.figure("Person trajectory")
vicon_ax = vicon_fig.add_subplot(111, projection='3d')
vicon_ax.plot(xs=vicon_person_data.pos_x, ys=vicon_person_data.pos_y, zs=vicon_person_data.pos_z)

combined_fig = plt.figure()
combined_ax = combined_fig.add_subplot(111)
combined_ax.plot(merged_data.index, -merged_data.dist_raw, label="TMOS dist raw")
combined_ax.plot(merged_data.index, -merged_data.dist_filt, label="TMOS dist filtered")
combined_ax.plot(merged_data.index, merged_data.true_dist, label="True distance")
# combined_ax.plot(dist.index, -derivative, label="True gradient (velocity)")
combined_ax.plot(merged_data.index, merged_data.vel, label="Velocity")
plt.grid(True)
plt.legend()'''

print(merged_data.dist_raw.min())

# merged_data.true_dist = merged_data.true_dist - merged_data.true_dist.min()

# merged_data.dist_raw = (merged_data.dist_raw - merged_data.dist_raw.min())

# merged_data = merged_data[(merged_data.index > 2) & (merged_data.index < 23.5)]

# Distance Error
error_fig = plt.figure("ERROR")
error_ax = error_fig.add_subplot(111)
#error_ax.plot(np.log(merged_data.dist_raw), merged_data.true_dist, label="TMOS dist raw")

#error_ax.plot(merged_data.dist_raw, merged_data.true_dist, label="TMOS dist raw")
#error_ax.plot(merged_data.dist_raw, 1380 * np.exp(0.00074212736 * merged_data.dist_raw) + 200, label="TMOS dist raw")

error_ax.plot(merged_data.index, merged_data.dist_raw, label="TMOS dist raw")
error_ax.plot(merged_data.index, merged_data.true_dist, label="True distance")
error_ax.plot(merged_data.index, 1380 * np.exp(0.00074212736 * merged_data.dist_raw) + 200, label="True distance 2")

# error_ax.plot(merged_data.index, normalize_data(merged_data.dist_raw / merged_data.true_dist), label="Distance diff error")
# error_ax.plot(merged_data.index, np.gradient(merged_data.true_dist - (-merged_data.dist_raw), merged_data.index), label="Gradient")
plt.grid(True)
plt.legend()

plt.show()
