import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def euclidean_distance(df1, df2, cols=None):
    if cols is None:
        cols = ['pos_x', 'pos_y']
    return np.linalg.norm(df1[cols].values - df2[cols].values, axis=1)


def normalize_data(df1, lim=1000):
    return lim * (df1 - df1.min()) / (df1.max() - df1.min())


''' TMOS '''
# Get the data
tmos_1_col_names = ["col_2", "in_time", "col_4", "temp", "col_6", "col_7", "col_8", "col_9"]
tmos_1_data = pd.read_csv("output/EXPERIMENT_SENSOR_2_CHARACT_SENSOR_1.log", names=tmos_1_col_names, index_col=0)
tmos_1_data.index = tmos_1_data.index / 1000.0
# tmos_1_data = normalize_data(tmos_1_data)

tmos_fig = plt.figure()
tmos_ax = tmos_fig.add_subplot(111)
tmos_ax.plot(tmos_1_data.index, tmos_1_data.col_4)
tmos_ax.plot(tmos_1_data.index, tmos_1_data.col_6)

#tmos_ax.plot(tmos_1_data.index, tmos_1_data.col_7)

''' VICON '''
vicon_col_names = ["obj", "pos_x", "pos_y", "pos_z"]
vicon_data = pd.read_csv("output/EXPERIMENT_SENSOR_2_CHARACT_VICON.log", names=vicon_col_names, index_col=0,
                         dtype={'obj': object})
vicon_data.index = vicon_data.index / 1000.0

TMOS_data = vicon_data.loc[vicon_data.obj == 'TMOS']
TMOS_data = TMOS_data[~((TMOS_data.pos_x == 0) & (TMOS_data.pos_y == 0) & (TMOS_data.pos_z == 0))]

PERSON_data = vicon_data.loc[vicon_data.obj == 'Person']
PERSON_data = PERSON_data[~((PERSON_data.pos_x == 0) & (PERSON_data.pos_y == 0) & (PERSON_data.pos_z == 0))]

vicon_fig = plt.figure()
vicon_ax = vicon_fig.add_subplot(111, projection='3d')
vicon_ax.plot(xs=PERSON_data.pos_x, ys=PERSON_data.pos_y, zs=PERSON_data.pos_z)

''' DISTANCE '''
dist = pd.DataFrame(data=euclidean_distance(PERSON_data, TMOS_data.mean()), index=PERSON_data.index, columns=['dist'])
dist = normalize_data(dist)

# Better tmos_1_data
print(tmos_1_data.col_6.max())
processed_tmos_1_data = -tmos_1_data.col_6  # tmos_1_data.col_6.max() - tmos_1_data.col_6
processed_tmos_1_data = normalize_data(processed_tmos_1_data)

processed_raw = normalize_data(-tmos_1_data.col_4)

combined_fig = plt.figure()
combined_ax = combined_fig.add_subplot(111)
# combined_ax.plot(tmos_1_data.index, tmos_1_data.col_4, label="Not filtered")
# combined_ax.plot(tmos_1_data.index, tmos_1_data.col_6, label="Filtered")
combined_ax.plot(tmos_1_data.index, processed_tmos_1_data, label="Better filtered")
combined_ax.plot(dist.index, dist.dist, label="True distance")
combined_ax.plot(tmos_1_data.index, tmos_1_data.col_7, label="Speed")
combined_ax.plot(tmos_1_data.index, processed_raw, label="Speed")
plt.legend()

plt.show()
