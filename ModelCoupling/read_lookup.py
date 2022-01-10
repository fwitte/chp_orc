
import numpy as np
import pandas as pd
from scipy import interpolate


data = pd.read_csv("Power_QT_lookup.csv", index_col=0)

T_range = data.columns.values.astype(float)
Q_range = data.index.values.astype(float)

f = interpolate.interp2d(T_range, Q_range, data.values, kind='cubic')

T_array = np.random.random_integers(97, 107, 100)
Q_array = np.random.random_integers(-10e5, -1e5, 100)
for T, Q in zip(T_array, Q_array):
    print(f(T, Q))
