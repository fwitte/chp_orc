# %%


from CoolProp.CoolProp import PropsSI
import pygmo as pg
import pandas as pd
from matplotlib import pyplot as plt
from orc import ORC_without_ihe, CHPORC
from tespy.components import HeatExchanger, Merge, Pump, Sink, Source, Splitter
from tespy.components.heat_exchangers.condenser import Condenser
from tespy.connections import Bus, Connection, Ref
from tespy.networks import Network
from opt import MultivariateOptimizationProblem
import json
import sys
import os

def variant_4(baseplant):

    # district heating system
    dh_return_temperature = 60
    dh_feed_temperature = 40
    dh_pressure = 5

    # components
    geo_splitter = Splitter("geo splitter")
    geo_merge = Merge("geo merge")

    # pump for district heating system?
    dh_source = Source("dh return")
    dh_sink = Sink("dh feed")
    dh_heat_exchanger = HeatExchanger("dh heat exchanger")

    baseplant.nw.del_conns(*baseplant.nw.get_conn(["22", "27"]))

    c22 = Connection(baseplant.nw.get_comp("evaporator"), "out1", geo_splitter, "in1", label="22")

    # district heating
    c23 = Connection(geo_splitter, "out1", dh_heat_exchanger, "in1", label="23")
    c24 = Connection(dh_heat_exchanger, "out1", geo_merge, "in1", label="24")

    # orc
    c25 = Connection(geo_splitter, "out2", baseplant.nw.get_comp("preheater"), "in1", label="25")
    c26 = Connection(baseplant.nw.get_comp("preheater"), "out1", geo_merge, "in2", label="26")

    c27 = Connection(
        geo_merge, "out1", baseplant.nw.get_comp("geo re-injection"), "in1", label="27"
    )
    baseplant.nw.add_conns(c22, c23, c24, c25, c26, c27)

    # district heating
    c31 = Connection(dh_source, "out1", dh_heat_exchanger, "in2", label="31")
    c32 = Connection(dh_heat_exchanger, "out2", dh_sink, "in1", label="32")

    baseplant.nw.add_conns(c31, c32)

    # no pr1 required, parallel to preheater
    dh_heat_exchanger.set_attr(pr2=0.98)
    c31.set_attr(
        fluid={baseplant.working_fluid: 0, "water": 1}, T=dh_feed_temperature, p=dh_pressure
    )
    c32.set_attr(T=dh_return_temperature)

    # reinjection temperature specification
    c26.set_attr(T=70)
    c24.set_attr(T=70)

    # solve the network
    baseplant.nw.solve("design")
    baseplant.nw.print_results()


def variant_3(nw):

    # district heating system
    dh_return_temperature = 60
    dh_feed_temperature = 40
    dh_pressure = 5

    # components
    geo_splitter = Splitter("geo splitter")
    geo_merge = Merge("geo merge")

    # pump for district heating system?
    dh_source = Source("dh return")
    dh_sink = Sink("dh feed")
    dh_heat_exchanger1 = HeatExchanger("dh heat exchanger 1")
    dh_heat_exchanger2 = HeatExchanger("dh heat exchanger 2")

    nw.del_conns(*nw.get_conn(["21", "27"]))

    c21_0 = Connection(
        nw.get_comp("geo source"), "out1", geo_splitter, "in1", label="21_0"
    )
    c21_1 = Connection(
        geo_splitter, "out1", nw.get_comp("evaporator"), "in1", label="21_1"
    )
    c23 = Connection(geo_splitter, "out2", dh_heat_exchanger2, "in1", label="23")

    # district heating
    c24 = Connection(dh_heat_exchanger2, "out1", geo_merge, "in1", label="24")
    c25 = Connection(
        nw.get_comp("preheater"), "out1", dh_heat_exchanger1, "in1", label="25"
    )
    c26 = Connection(dh_heat_exchanger1, "out1", geo_merge, "in2", label="26")

    c27 = Connection(
        geo_merge, "out1", nw.get_comp("geo re-injection"), "in1", label="27"
    )
    nw.add_conns(c21_0, c21_1, c23, c24, c25, c26, c27)

    # district heating
    c31 = Connection(dh_source, "out1", dh_heat_exchanger1, "in2", label="31")
    c32 = Connection(dh_heat_exchanger1, "out2", dh_heat_exchanger2, "in2", label="32")
    c33 = Connection(dh_heat_exchanger2, "out2", dh_sink, "in1", label="33")

    nw.add_conns(c31, c32, c33)

    dh_heat_exchanger1.set_attr(pr1=0.98, pr2=0.98)
    # no pr1 required, parallel to ORC/dh_heat_exchanger1
    dh_heat_exchanger2.set_attr(pr2=0.98)
    c21_0.set_attr(fluid={working_fluid: 0, "water": 1}, T=100, p=25, m=10)
    c31.set_attr(
        fluid={working_fluid: 0, "water": 1}, T=dh_feed_temperature, p=dh_pressure
    )
    c32.set_attr(T=(dh_feed_temperature + dh_return_temperature) / 2)
    c33.set_attr(T=dh_return_temperature)

    # reinjection temperature specification
    c26.set_attr(T=70)
    c24.set_attr(T=70)

    # solve the network
    nw.solve("design")

    P = []
    Q = []
    T_range = [42, 44, 46, 48, 50, 52, 54, 56, 58]
    for T in T_range:
        c32.set_attr(T=T)
        nw.solve("design")
        P += [abs(nw.get_comp("turbine").P.val)]
        Q += [abs(dh_heat_exchanger1.Q.val + dh_heat_exchanger2.Q.val)]

    fig, ax = plt.subplots(2, 1)
    ax[0].plot(T_range, P)
    ax[0].grid()
    ax[0].set_ylabel("Turbine power")
    ax[1].plot(T_range, Q)
    ax[1].grid()
    ax[1].set_xlabel("Temperature between heat exchangers")
    ax[1].set_ylabel("District heating system heat")
    fig.savefig(working_fluid + ".png")
    plt.close()

# create base plant and supply functionalities
plant = CHPORC("R134a")
# modify the plant structure
variant_4(plant)
# solve mode with specified parameters
plant.nw.print_results()


# make a trivial test:
# -(un)specifiy some boundary conditions
# -set some connection and component variables
# -set a lower limit constraint

with open(sys.argv[1], 'r') as f:
    input_data = json.load(f)
    f.close()

boundary_conditions = input_data['boundary_conditions']
variables = input_data['variables']
constraints = input_data['constraints']
objective = input_data['objective']

plant.set_params(**boundary_conditions)

num_gen = input_data['num_gen']
num_ind = input_data['num_ind']
# this should be outside of the optimitzation class

optimize = MultivariateOptimizationProblem(plant, variables, constraints, objective)

# this must be outside of
algo = pg.ihs(gen=num_gen)
optimize.run(algo, num_ind, num_gen)

print(optimize.individuals)

path = input_data['scenario_name'] + '/'

if not os.path.isdir(path):
    os.mkdir(path)

optimize.individuals.to_csv(input_data['scenario_name'] + '/result.csv')
# write optimization instance data to json file for postprocessing

variables_labels = {}
for obj, data in optimize.variables.items():
    for label, params in data.items():
        for param in params:
            variables_labels[obj + '-' + label + '-' + param] = param + ' at ' + obj + ' ' + label


with open(input_data['scenario_name'] + '/problem.json', 'w') as f:
    output = {
        key + "_list": optimize.__dict__[key + "_list"]
        for key in ["constraint", "variable", "objective"]
    }
    output.update(variables_labels)
    f.write(json.dumps(output))
    f.close()