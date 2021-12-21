#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import json
from scipy import interpolate
import logging
from tespy.networks import load_network
from tespy.tools import logger
from tespy.connections import Ref
from tespy.tools.helpers import TESPyNetworkError
from tespy.tools import document_model

logger.define_logging(
    log_path=True, log_version=True, screen_level=logging.WARNING, file_level=logging.WARNING
)


class PowerPlantModel:
    """
    Class for a power plant model within a coupled loop.

    Parameters
    ----------
    path : str
        Path to exported tespy model
    """

    def __init__(self, path):

        self.path = path
        self.load_tespy_model()

    def load_tespy_model(self):

        self.nw = load_network(self.path)
        self.nw.set_attr(iterinfo=False)
        self.nw.solve('design', init_only=True)

    def get_parameters(self, **kwargs):

        result = kwargs.copy()
        if "Connections" in kwargs:
            for c, params in kwargs["Connections"].items():
                for param in params:
                    result["Connections"][c][param] = self.nw.get_conn(c).get_attr(param)

        if "Components" in kwargs:
            for c, params in kwargs["Components"].items():
                for param in params:
                    result["Components"][c][param] = self.nw.get_comp(c).get_attr(param)

    def get_single_parameter(self, obj, label, parameter):
        if obj == 'Components':
            return self.nw.get_comp(label).get_attr(parameter).val
        elif obj == 'Connections':
            return self.nw.get_conn(label).get_attr(parameter).val

    def set_parameters(self, **kwargs):

        if "Connections" in kwargs:
            for c, params in kwargs["Connections"].items():
                self.nw.get_conn(c).set_attr(**params)

        if "Components" in kwargs:
            for c, params in kwargs["Components"].items():
                self.nw.get_comp(c).set_attr(**params)

    def set_single_parameter(self, obj, label, parameter, value):
        if obj == 'Components':
            self.nw.get_comp(label).set_attr({parameter: value})
        elif obj == 'Connections':
            self.nw.get_conn(label).get_attr({parameter: value})

    def run(self, **kwargs):

        self.set_parameters(**kwargs)

        self.solved = False
        try:
            self.nw.solve("offdesign", design_path=self.path)
            if self.nw.res[-1] >= 1e-3 or self.nw.lin_dep:
                self.nw.solve(
                    "offdesign", init_only=True, init_path=self.path,
                    design_path=self.path
                )
            else:
                if any(self.nw.results['HeatExchanger']['Q'] > 0):
                    self.solved = False
                else:
                    self.solved = True
        except ValueError as e:
            print(e)
            print("The iteration failed")
            self.nw.lin_dep = True
            self.nw.solve(
                "offdesign", init_only=True, init_path=self.path,
                design_path=self.path
            )
