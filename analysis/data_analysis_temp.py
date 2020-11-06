import os
import sys
sys.path.extend([os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + os.sep + os.pardir)])

import matplotlib.pyplot as plt

from analysis import data_functions


''' GET DATA '''
tmos_data_new = data_functions.get_data_from_file("../output/temp/TEMP_SIMULT_MAXDIST_32")

''' LINEAR TEMP FIT '''
fit_func_1 = data_functions.get_fit_func(tmos_data_new["tmos1"].temp, tmos_data_new["tmos1"].dist_raw, 1)
fit_func_2 = data_functions.get_fit_func(tmos_data_new["tmos2"].temp, tmos_data_new["tmos2"].dist_raw, 1)
fit_func_3 = data_functions.get_fit_func(tmos_data_new["tmos3"].temp, tmos_data_new["tmos3"].dist_raw, 1)
fit_func_4 = data_functions.get_fit_func(tmos_data_new["tmos4"].temp, tmos_data_new["tmos4"].dist_raw, 1)
print(fit_func_1.coef[0])
print(fit_func_2.coef[0])
print(fit_func_3.coef[0])
print(fit_func_4.coef[0])

fig3 = plt.figure("Sensor comparison")
ax2 = fig3.add_subplot(111)
ax2.plot(tmos_data_new["tmos1"].temp, tmos_data_new["tmos1"].dist_raw, label="TMOS 1")
ax2.plot(tmos_data_new["tmos2"].temp, tmos_data_new["tmos2"].dist_raw, label="TMOS 2")
ax2.plot(tmos_data_new["tmos3"].temp, tmos_data_new["tmos3"].dist_raw, label="TMOS 3")
ax2.plot(tmos_data_new["tmos4"].temp, tmos_data_new["tmos4"].dist_raw, label="TMOS 4")

ax2.plot(tmos_data_new["tmos1"].temp, data_functions.compensate_temp(tmos_data_new["tmos1"].dist_raw, tmos_data_new["tmos1"].temp, fit_func_1.coef[0]), label="Sensor data [TMOS 1 TEMP]")
ax2.plot(tmos_data_new["tmos2"].temp, data_functions.compensate_temp(tmos_data_new["tmos2"].dist_raw, tmos_data_new["tmos2"].temp, fit_func_2.coef[0]), label="Sensor data [TMOS 2 TEMP]")
ax2.plot(tmos_data_new["tmos3"].temp, data_functions.compensate_temp(tmos_data_new["tmos3"].dist_raw, tmos_data_new["tmos3"].temp, fit_func_3.coef[0]), label="Sensor data [TMOS 3 TEMP]")
ax2.plot(tmos_data_new["tmos4"].temp, data_functions.compensate_temp(tmos_data_new["tmos4"].dist_raw, tmos_data_new["tmos4"].temp, fit_func_4.coef[0]), label="Sensor data [TMOS 4 TEMP]")

ax2.set_title("Sensor comparison")
ax2.set_xlabel("Temperature")
ax2.set_ylabel("Sensor reading")
ax2.grid(True)
ax2.legend()


plt.show()

