import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from scipy.optimize import curve_fit
from sklearn import linear_model as LM
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import f1_score, recall_score
from sklearn.neural_network import MLPClassifier


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


def estimated_distance(x, coef):
    return coef[0] * x + coef[1] * np.power(x, 2) + coef[2] * np.exp(x) + 20


''' GET DATA '''
# TMOS
tmos_col_names = ["col_2", "in_time", "dist_raw", "temp", "dist_filt", "vel", "bin_1", "bin_2"]
tmos_data = pd.read_csv("output/2_Sensor.log", names=tmos_col_names, index_col=0)
tmos_data.index = tmos_data.index / 1000
tmos_data.dist_raw = -tmos_data.dist_raw
tmos_data.dist_filt = -tmos_data.dist_filt
# tmos_data.dist_raw = np.append([0, 0, 0, 0], pd.Series(tmos_data.dist_raw).rolling(window=5).mean().iloc[5 - 1:].values)

# Vicon
vicon_col_names = ["obj", "pos_x", "pos_y", "pos_z"]
vicon_data = pd.read_csv("output/2_Vicon.log", names=vicon_col_names, index_col=0,
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
                               index=vicon_person_data.index, columns=['dist_true'])

''' MERGE ALL DATA '''
merged_data = pd.concat([vicon_true_dist, tmos_data], axis=1)
merged_data = merged_data.interpolate().ffill().bfill()  # Match data on index and fill NaNs

merged_data["shifted"] = merged_data.shift(periods=-85).dist_filt

# Filter out ambiguous parts
merged_data = merged_data[(merged_data.index > 5) & (merged_data.index < 23.3)]

merged_data.dist_true = merged_data.dist_true / 100
merged_data.shifted = merged_data.shifted / 100

#####################################################################################################################
print("-------TRAINING-------")
data_train = np.array(merged_data.shifted.values)
data_train = data_train.reshape(-1, 1)

p1 = np.power(data_train, 2)
p2 = np.exp(data_train)
p3 = np.ones((data_train.shape[0], 1))

data_train = np.append(data_train, p1, axis=1)
data_train = np.append(data_train, p2, axis=1)
data_train = np.append(data_train, p3, axis=1)

print(data_train)

# Create linear regression object
regr = LM.RidgeCV(cv=10, fit_intercept=True)
# Train the model using the training set
regr.fit(data_train, merged_data.dist_true.values)

print(regr.coef_)
#####################################################################################################################


# Curve fit
#popt, _ = curve_fit(lin_fit, merged_data.shifted, np.log(merged_data.dist_true), maxfev=100000)
#print("Fitted parameters: ", popt)

fitted_param = np.polyfit(merged_data.shifted, np.log(merged_data.dist_true), 5)
fit_func = np.poly1d(fitted_param)
print(fitted_param)

fig, error_ax = plt.subplots(2)
error_ax[0].plot(merged_data.shifted, np.log(merged_data.dist_true))
error_ax[0].plot(merged_data.shifted, fit_func(merged_data.shifted))

error_ax[1].plot(merged_data.shifted, merged_data.dist_true)
error_ax[1].plot(merged_data.shifted, np.exp(fit_func(merged_data.shifted)))
# error_ax.plot(merged_data_shifted.dist_filt, -1000000/merged_data_shifted.dist_filt)

fig, combined_ax = plt.subplots(2)
#combined_ax[0].plot(merged_data.index, merged_data.dist_raw, label="TMOS dist raw")
#combined_ax[0].plot(merged_data.index, merged_data.dist_filt, label="TMOS dist filtered")
combined_ax[0].plot(merged_data.index, merged_data.shifted, label="TMOS dist filtered (shift)")
combined_ax[0].plot(merged_data.index, np.exp(fit_func(merged_data.shifted)), label="Estimated distance")
combined_ax[0].plot(merged_data.index, merged_data.dist_true, label="True distance")
combined_ax[0].grid(True)
combined_ax[0].legend()

combined_ax[1].plot(merged_data.index, merged_data.temp, label="Temp")

plt.show()
