# create variant 4 export
from orc import CHPORC
import numpy as np

###
# set up plant
plant = CHPORC("Isopentane")
plant.high_temperature_dh()

plant.nw.save("design_state_" + plant.working_fluid)
plant.design_path = "design_state_" + plant.working_fluid
plant.solve_offdesign()


###

plant2 = CHPORC("Isopentane")
plant2.low_temperature_dh()


plant2.solve_design(**{"Connections": {"27": {"T": 90}, "6": {"T": None}}})
plant2.nw.print_results()

plant2.nw.save("design_state_" + plant2.working_fluid)
plant2.design_path = "design_state_" + plant2.working_fluid
plant2.solve_offdesign()

# # set to desired design state
# T_prod = 100

# plant.solve_design(**{
#     "Connections": {
#         "21": {"T": T_prod, "m": None}
#     },
#     "Components": {"dh heat exchanger": {"Q": -1e6}}
# })

# # save data
# plant.nw.save("design_state_" + plant.working_fluid)
# plant.design_path = "design_state_" + plant.working_fluid
# plant.nw.print_results()

# # test solve offdesign state
# plant.solve_offdesign()

# m_prod = plant.get_single_parameter("Connections", "21", "m")

# plant.set_parameters()
# plant.solve_offdesign(**{
#     "Connections": {
#         "21": {"m": m_prod},
#         "24": {"m": None}
#     },
#     "Components": {"dh heat exchanger": {"Q": -10e5}}
# })

# grid_num = 6
# Q_range = np.linspace(-10, -1, grid_num) * 1e5
# T_range = np.linspace(97, 107, grid_num)

# # plant.set_parameters(**{"Connections": {"24": {"design": []}}})

# power_data = pd.DataFrame(columns=T_range, index=Q_range)

# for Q in Q_range:
#     for T in T_range:
#         plant.solve_offdesign(**{
#             "Components": {"dh heat exchanger": {"Q": Q}},
#             "Connections": {"21": {"T": T}},
#         })
#         # m = plant.get_single_parameter("Connections", "24", "m")
#         T1 = plant.get_single_parameter("Connections", "24", "T")
#         T2 = plant.get_single_parameter("Connections", "26", "T")
#         T3 = plant.get_single_parameter("Connections", "27", "T")
#         print(T1, T2, T3)
#         P = plant.get_single_parameter("Components", "turbine", "P")
#         # if T1 < 65:
#         #     plant.solve_offdesign(**{
#         #         "Connections": {"24": {"T": 65}, "32": {"T": None}},
#         #     })

#         # T1 = plant.get_single_parameter("Connections", "24", "T")
#         # T3 = plant.get_single_parameter("Connections", "32", "T")
#         # print(m, P, Q, T1, T2)
#         # plant.set_parameters(**{
#         #     "Connections": {"24": {"T": None}, "32": {"T": 60}},
#         # })
#         power_data.loc[Q, T] = P

# power_data.to_csv("Power_QT_lookup.csv")

# from scipy import interpolate

# f = interpolate.interp2d(T_range, Q_range, power_data.values, kind='cubic')

# T_array = np.random.random_integers(97, 107, 100)
# Q_array = np.random.random_integers(-10e5, -1e5, 100)
# for T, Q in zip(T_array, Q_array):
#     print(f(T, Q))

# model.set_parameters(**{"Components": {"dh heat exchanger": {"Q": -3e5}}})
# model.run()
# print(model.get_single_parameter("Components", "turbine", "P"))

# model.set_parameters(**{"Components": {"dh heat exchanger": {"Q": -2e5}}})
# model.run()
# print(model.get_single_parameter("Components", "turbine", "P"))

# # dataframes to save data
# turbine_power = pd.DataFrame()
# dh_heat_output = pd.DataFrame()
# return_temperature = pd.DataFrame()

# # temperature range to check in model
# temperature_range = np.linspace(100, 120, 7)
# # mass flow from 10 -> 11 (include 10)
# massflow_range = np.linspace(10, 11, 3)

# # iterate over temperature and mass flow
# for T in temperature_range:
#     for m in massflow_range:
#         model.set_parameters(**{"Connections": {"21": {"T": T, "m": m}}})
#         model.run()

#         if model.solved:
#             turbine_power.loc[T, m] = model.get_single_parameter("Components", "turbine", "P")
#             dh_heat_output.loc[T, m] = model.get_single_parameter("Components", "dh heat exchanger", "Q")
#             return_temperature.loc[T, m] = model.get_single_parameter("Connections", "27", "T")


# # mass flow from 10 -> 8 (exclude 10)
# massflow_range = np.linspace(8, 10, 4, endpoint=False)[::-1]
# # set starting values back to design point
# model.nw.solve("offdesign", design_path="design_state_R134a", init_path="design_state_R134a", init_only=True)

# for T in temperature_range:
#     for m in massflow_range:
#         model.set_parameters(**{"Connections": {"21": {"T": T, "m": m}}})
#         model.run()

#         if model.solved:
#             turbine_power.loc[T, m] = model.get_single_parameter("Components", "turbine", "P")
#             dh_heat_output.loc[T, m] = model.get_single_parameter("Components", "dh heat exchanger", "Q")
#             return_temperature.loc[T, m] = model.get_single_parameter("Connections", "27", "T")

# turbine_power = turbine_power[sorted(turbine_power.columns)]
# dh_heat_output = dh_heat_output[sorted(dh_heat_output.columns)]
# return_temperature = return_temperature[sorted(return_temperature.columns)]

# print(turbine_power)
# print(dh_heat_output)
# print(return_temperature)

# ToDo:
# - decide what the lookup should look like (linear or splines)
#   -> for linear lookup see: https://github.com/oemof/tespy/blob/e32b16bc5852b318d760ca0b6488f88f5b05e917/src/tespy/tools/characteristics.py#L190-L342
#   -> for splines see: https://github.com/oemof/tespy/blob/e32b16bc5852b318d760ca0b6488f88f5b05e917/src/tespy/tools/fluid_properties.py#L39-L290
# - implement respective lookup table functionalities
# - do we need reverse lookup?
#   -> Suggest Newton search on lookup, see: https://github.com/oemof/tespy/blob/e32b16bc5852b318d760ca0b6488f88f5b05e917/src/tespy/tools/fluid_properties.py#L584-L586
