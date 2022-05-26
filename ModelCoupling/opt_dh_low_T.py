
import numpy as np
import pandas as pd
import pygmo as pg
from tespy.tools import OptimizationProblem
import sys
import json
import os
from orc import CHPORC


plant = CHPORC("Isopentane")
plant.low_temperature_dh()

with open(sys.argv[1], 'r') as f:
    input_data = json.load(f)
    f.close()

boundary_conditions = input_data['boundary_conditions']
variables = input_data['variables']
constraints = input_data['constraints']
objective = input_data['objective']

plant.set_parameters(**boundary_conditions)

num_gen = input_data['num_gen']
num_ind = input_data['num_ind']
# this should be outside of the optimitzation class

optimize = OptimizationProblem(plant, variables, constraints, objective)

# this must be outside of
algo = pg.pso(gen=num_gen)
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
