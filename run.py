import pandas as pd
from orc import CHPORC
import sys
import json
import os


with open(sys.argv[-1], "r") as f:
    input_data = json.load(f)
    f.close()


path = "./results/"
os.makedirs(path, exist_ok=True)


# read ambient data: geo temperature time series
geo_data = pd.read_excel(
    "input/production_data_geo.xlsx",
    sheet_name=["well_temps", "lake_temp"], index_col=0
)

well_data = geo_data["well_temps"]
lake_data = geo_data["lake_temp"]

demand_data = pd.read_csv("input/Demand profile_NewTown.csv", index_col=0)
demand_data["month_integer"] = list(range(len(demand_data.index)))

demand_data.sort_values(by="percent", ascending=False, inplace=True)
heat_max = demand_data["percent"].max()
num_quarters = len(well_data.index)


T_prod_design = input_data["T_geo_design"]
T_lake_design = demand_data["T_lake"].mean()
Q_design = input_data["Q_design"]

# set to desired design state
for mass_flow in well_data.columns:

    scn_name = input_data["scenario"] + "_" + str(int(mass_flow))

    result = pd.DataFrame(
        index=range(num_quarters * 3),
        columns=[
            "T_geo", "T_lake", "heat", "power",
            "heat_lake", "heat_input", "T_24", "T_26", "T_dh_feed"
        ]
    )

    # set up new plant
    plant = CHPORC(input_data["working_fluid"])
    # create variant 4 export
    plant.insert_dh_and_cw()

    lake_intake = plant.nw.get_conn("11")
    lake_outflow = plant.nw.get_conn("13")

    geo_inflow = plant.nw.get_conn("21")
    geo_outflow = plant.nw.get_conn("27")

    plant.solve_design(**{
        "Connections": {
            "6": {"T": None},
            "11": {"T": T_lake_design},
            "13": {"T": T_lake_design + 10},
            "21": {"T": T_prod_design, "m": mass_flow},
            "24": {"T": input_data["T_reinjection"]},
            "26": {"T": input_data["T_reinjection"]},
            "31": {"T": input_data["T_dh_return"]},
            "32": {"T": input_data["T_dh_feed"]},
        },
        "Components": {
            "dh heat exchanger": {"Q": Q_design},
            "valve": {"pr": 0.75}
        }
    })

    # save data
    plant.nw.save("design_state_" + scn_name)
    plant.design_path = "design_state_" + scn_name
    plant.nw.print_results()

    # test solve offdesign state
    plant.solve_offdesign(**{
        "Connections": {
            "26": {"m": None, "T": input_data["T_reinjection"]},
            "32": {"T": None},
        },
        "Components": {
            "valve": {"design": [], "pr": None}
        }})

    for index, row in demand_data.iterrows():
        heat_percent = row["percent"]
        T_lake = row["T_lake"]
        quarter = int(row["month_integer"] // 3)
        year = 0
        for T_geo in well_data[mass_flow].iloc[quarter::4]:
            # print(heat_percent / heat_max * Q_design, T_lake, T_geo)
            plant.solve_offdesign(**{
                "Connections": {
                    "11": {"T": T_lake},
                    "21": {"T": T_geo},
                    "26": {"T": input_data["T_reinjection"]},
                    "13": {"T": T_lake + 10}
                },
                "Components": {
                    "dh heat exchanger": {"Q": heat_percent / heat_max * Q_design},
                    "valve": {"pr": None},
                }})
            if plant.nw.get_comp("valve").pr.val > 1:
                plant.solve_offdesign(**{
                    "Connections": {
                        "26": {"T": None}
                    },
                    "Components": {
                        "valve": {"pr": 1},
                    }
                })

            idx = year * 12 + row["month_integer"]
            result.loc[idx, "heat"] = plant.heat_bus.P.val
            result.loc[idx, "power"] = plant.power_bus.P.val
            result.loc[idx, "T_lake"] = T_lake
            result.loc[idx, "T_geo"] = T_geo
            result.loc[idx, "heat_lake"] = lake_intake.m.val_SI * (
                lake_outflow.h.val_SI - lake_intake.h.val_SI
            )
            result.loc[idx, "T_24"] = plant.nw.get_conn("24").T.val
            result.loc[idx, "T_26"] = plant.nw.get_conn("26").T.val
            result.loc[idx, "T_dh_feed"] = plant.nw.get_conn("32").T.val
            result.loc[idx, "heat_input"] = geo_inflow.m.val_SI * (
                geo_outflow.h.val_SI - geo_inflow.h.val_SI
            )

            year += 1

    result.to_csv("results/Productiondata_" + scn_name + ".csv")
