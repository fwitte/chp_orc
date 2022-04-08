
from imp import init_builtin
import numpy as np
import pandas as pd

# ToDo: verify model design and offdesign specifications
geo_data = pd.read_excel("production_data_geo.xlsx", sheet_name=["well_temps", "lake_temp"], index_col=0)

well_data = geo_data["well_temps"]
lake_data = geo_data["lake_temp"]

# create variant 4 export
from orc import CHPORC

# set up plant
plant = CHPORC("R134a")
plant.variant_4()

# set to desired design state
mass_flow = 50
T_prod_design = well_data[mass_flow].mean()
T_lake_design = lake_data["Average C"].mean()

plant.solve_design(**{
    "Connections": {
        "6": {"T": T_prod_design - 15},
        "11": {"T": T_lake_design},
        "13": {"T": 25},
        "21": {"T": T_prod_design, "m": mass_flow},
        "24": {"T": 75, "m": None},
        "26": {"T": 75},
    }
})

# save data
plant.nw.save("design_state_" + plant.working_fluid)
plant.design_path = "design_state_" + plant.working_fluid
plant.nw.print_results()

# test solve offdesign state
plant.solve_offdesign()

m_prod = plant.get_single_parameter("Connections", "21", "m")

plant.set_parameters()
plant.solve_offdesign()

plant.nw.save('intermediate_stable')

grid_num = 6
T_prod_range = np.linspace(well_data[mass_flow].min(), well_data[mass_flow].max(), grid_num)
T_lake_range = np.linspace(lake_data["Average C"].min(), lake_data["Average C"].max(), grid_num)

orc_power = pd.DataFrame(columns=T_lake_range, index=T_prod_range)
orc_heat = orc_power.copy()

for T_prod in T_prod_range:
    for T_lake in T_lake_range:
        if T_lake == T_lake_range[0]:
            plant.solve_offdesign(init_path="intermediate_stable", **{
                "Connections": {"21": {"T": T_prod}, "11": {"T": T_lake}},
            })
            plant.nw.save('intermediate_stable')
        else:
            plant.solve_offdesign(**{
                "Connections": {"21": {"T": T_prod}, "11": {"T": T_lake}},
            })

        restricted = False
        mr_lw = plant.nw.get_conn('13').m.val_SI / plant.nw.get_conn('13').m.design
        if mr_lw > 1.5:

            m_iterator = np.arange(
                plant.nw.get_conn('13').m.design * 1.5,
                plant.nw.get_conn('13').m.val_SI, 20
            )
            for m in m_iterator[::-1]:
                plant.solve_offdesign(**{
                    "Connections": {"26": {"T": None}, "13": {"m": m}},
                })
            restricted = True

        m_dh = plant.get_single_parameter("Connections", "24", "m")
        m_ph = plant.get_single_parameter("Connections", "26", "m")
        T_ph = plant.get_single_parameter("Connections", "26", "T")
        T_reinj = plant.get_single_parameter("Connections", "27", "T")

        P = plant.get_single_parameter("Components", "turbine", "P")
        Q = plant.get_single_parameter("Components", "dh heat exchanger", "Q")

        orc_power.loc[T_prod, T_lake] = P
        orc_heat.loc[T_prod, T_lake] = Q

        if restricted:
            if T_lake != T_lake_range[-1]:
                for m in m_iterator:
                    plant.solve_offdesign(**{
                        "Connections": {"26": {"T": None}, "13": {"m": m}},
                    })
            plant.set_parameters(**{
                "Connections": {"26": {"T": 75}, "13": {"m": None}},
            })

orc_power.to_csv("ORC_Power_lookup.csv")
orc_heat.to_csv("ORC_Heat_lookup.csv")
