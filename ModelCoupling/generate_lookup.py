
import numpy as np
import pandas as pd

# ToDo: verify model design and offdesign specifications

# create variant 4 export
from orc import CHPORC

# set up plant
plant = CHPORC("R134a")
plant.variant_4()

# set to desired design state
T_prod = 100

plant.solve_design(**{
    "Connections": {
        "21": {"T": T_prod, "m": None}
    },
    "Components": {"dh heat exchanger": {"Q": -1e6}}
})

# save data
plant.nw.save("design_state_" + plant.working_fluid)
plant.design_path = "design_state_" + plant.working_fluid
plant.nw.print_results()

# test solve offdesign state
plant.solve_offdesign()

m_prod = plant.get_single_parameter("Connections", "21", "m")

plant.set_parameters()
plant.solve_offdesign(**{
    "Connections": {
        "21": {"m": m_prod},
        "24": {"m": None}
    },
    "Components": {"dh heat exchanger": {"Q": -10e5}}
})

grid_num = 6
Q_range = np.linspace(-10, -1, grid_num) * 1e5
T_range = np.linspace(97, 107, grid_num)

power_data = pd.DataFrame(columns=T_range, index=Q_range)

for Q in Q_range:
    for T in T_range:
        plant.solve_offdesign(**{
            "Components": {"dh heat exchanger": {"Q": Q}},
            "Connections": {"21": {"T": T}},
        })
        T1 = plant.get_single_parameter("Connections", "24", "T")
        T2 = plant.get_single_parameter("Connections", "26", "T")
        T3 = plant.get_single_parameter("Connections", "27", "T")
        # print(T1, T2, T3)

        P = plant.get_single_parameter("Components", "turbine", "P")
        power_data.loc[Q, T] = P

power_data.to_csv("Power_QT_lookup.csv")
