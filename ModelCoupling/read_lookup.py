
import numpy as np
import pandas as pd
from scipy import interpolate


data = pd.read_csv("ORC_Heat_lookup.csv", index_col=0)

T_well_range = data.index.values.astype(float)
T_lake_range = data.columns.values.astype(float)

heat = interpolate.interp2d(T_lake_range, T_well_range, data.values, kind='cubic')


data = pd.read_csv("ORC_Power_lookup.csv", index_col=0)

T_well_range = data.index.values.astype(float)
T_lake_range = data.columns.values.astype(float)

power = interpolate.interp2d(T_lake_range, T_well_range, data.values, kind='cubic')

T_well_array = np.random.randint(115, 135, 100)
T_lake_array = np.random.randint(2, 21, 100)
for T_well, T_lake in zip(T_well_array, T_lake_array):
    print(heat(T_lake, T_well))
    print(power(T_lake, T_well))
