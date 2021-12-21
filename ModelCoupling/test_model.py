from powerplant import PowerPlantModel
import numpy as np
import pandas as pd

# ToDo: verify model design and offdesign specifications

# create variant 4 export
from orc import CHPORC

plant = CHPORC("R134a")
plant.variant_4()

# import exported model
model = PowerPlantModel("design_state_R134a")
model.nw.solve("offdesign", design_path="design_state_R134a", init_path="design_state_R134a")
model.nw.print_results()

# dataframes to save data
turbine_power = pd.DataFrame()
dh_heat_output = pd.DataFrame()
return_temperature = pd.DataFrame()

# temperature range to check in model
temperature_range = np.linspace(100, 120, 7)
# mass flow from 10 -> 11 (include 10)
massflow_range = np.linspace(10, 11, 3)

# iterate over temperature and mass flow
for T in temperature_range:
    for m in massflow_range:
        model.set_parameters(**{"Connections": {"21": {"T": T, "m": m}}})
        model.run()

        if model.solved:
            turbine_power.loc[T, m] = model.get_single_parameter("Components", "turbine", "P")
            dh_heat_output.loc[T, m] = model.get_single_parameter("Components", "dh heat exchanger", "Q")
            return_temperature.loc[T, m] = model.get_single_parameter("Connections", "27", "T")


# mass flow from 10 -> 8 (exclude 10)
massflow_range = np.linspace(8, 10, 4, endpoint=False)[::-1]
# set starting values back to design point
model.nw.solve("offdesign", design_path="design_state_R134a", init_path="design_state_R134a", init_only=True)

for T in temperature_range:
    for m in massflow_range:
        model.set_parameters(**{"Connections": {"21": {"T": T, "m": m}}})
        model.run()

        if model.solved:
            turbine_power.loc[T, m] = model.get_single_parameter("Components", "turbine", "P")
            dh_heat_output.loc[T, m] = model.get_single_parameter("Components", "dh heat exchanger", "Q")
            return_temperature.loc[T, m] = model.get_single_parameter("Connections", "27", "T")

turbine_power = turbine_power[sorted(turbine_power.columns)]
dh_heat_output = dh_heat_output[sorted(dh_heat_output.columns)]
return_temperature = return_temperature[sorted(return_temperature.columns)]

print(turbine_power)
print(dh_heat_output)
print(return_temperature)

# ToDo:
# - decide what the lookup should look like (linear or splines)
#   -> for linear lookup see: https://github.com/oemof/tespy/blob/e32b16bc5852b318d760ca0b6488f88f5b05e917/src/tespy/tools/characteristics.py#L190-L342
#   -> for splines see: https://github.com/oemof/tespy/blob/e32b16bc5852b318d760ca0b6488f88f5b05e917/src/tespy/tools/fluid_properties.py#L39-L290
# - implement respective lookup table functionalities
# - do we need reverse lookup?
#   -> Suggest Newton search on lookup, see: https://github.com/oemof/tespy/blob/e32b16bc5852b318d760ca0b6488f88f5b05e917/src/tespy/tools/fluid_properties.py#L584-L586
