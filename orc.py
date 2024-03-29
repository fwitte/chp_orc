import numpy as np

from CoolProp.CoolProp import PropsSI
from tespy.components import (
    Condenser,
    CycleCloser,
    Drum,
    HeatExchanger,
    Merge,
    Pump,
    Sink,
    Source,
    Splitter,
    Turbine,
    Valve,
)
from tespy.components.subsystem import Subsystem
from tespy.connections import Connection, Ref, Bus
from tespy.networks import Network


class ORC_without_ihe(Subsystem):
    def create_comps(self):
        """Create the subsystem's components."""

        # main cycle
        self.comps["condenser"] = Condenser("condenser")
        self.comps["feed pump"] = Pump("feed pump")
        self.comps["preheater"] = HeatExchanger("preheater")
        self.comps["evaporator"] = HeatExchanger("evaporator")
        self.comps["drum"] = Drum("drum")
        self.comps["valve"] = Valve("valve")
        self.comps["turbine"] = Turbine("turbine")
        self.comps["orc cycle closer"] = CycleCloser("orc cycle closer")

    def create_conns(self):
        """Define the subsystem's connections."""

        # main cycle
        self.conns["0"] = Connection(
            self.comps["condenser"],
            "out1",
            self.comps["orc cycle closer"],
            "in1",
            label="0",
        )
        self.conns["1"] = Connection(
            self.comps["orc cycle closer"],
            "out1",
            self.comps["feed pump"],
            "in1",
            label="1",
        )
        self.conns["2"] = Connection(
            self.comps["feed pump"], "out1", self.comps["preheater"], "in2", label="2"
        )
        self.conns["3"] = Connection(
            self.comps["preheater"], "out2", self.comps["drum"], "in1", label="3"
        )
        self.conns["4"] = Connection(
            self.comps["drum"], "out1", self.comps["evaporator"], "in2", label="4"
        )
        self.conns["5"] = Connection(
            self.comps["evaporator"], "out2", self.comps["drum"], "in2", label="5"
        )
        self.conns["6"] = Connection(
            self.comps["drum"], "out2", self.comps["valve"], "in1", label="6"
        )
        self.conns["7"] = Connection(
            self.comps["valve"], "out1", self.comps["turbine"], "in1", label="7"
        )
        self.conns["8"] = Connection(
            self.comps["turbine"], "out1", self.comps["condenser"], "in1", label="8"
        )


class CHPORC:
    def __init__(self, working_fluid):

        self.working_fluid = working_fluid
        fluids = ["water", working_fluid]
        self.nw = Network(fluids=fluids)
        self.nw.set_attr(p_unit="bar", T_unit="C", h_unit="kJ / kg", iterinfo=False)

        # geo parameters
        geo_mass_flow = 50
        geo_temperature = 130
        geo_pressure = 25

        # lake water parameters & exergy analysis if required
        self.T0 = 15
        self.p0 = 1

        orc = ORC_without_ihe("orc")
        self.nw.add_subsys(orc)

        # pump for geo water?
        geo_source = Source("geo source")
        geo_sink = Sink("geo re-injection")

        dummy_source = Source("coolant source")
        dummy_sink = Sink("coolant sink")

        # Connections

        c11 = Connection(dummy_source, "out1", orc.comps["condenser"], "in2", label="11")
        c12 = Connection(orc.comps["condenser"], "out2", dummy_sink, "in1", label="12")

        # ORC only for stable starting values
        c21 = Connection(geo_source, "out1", orc.comps["evaporator"], "in1", label="21")
        c22 = Connection(orc.comps["evaporator"], "out1", orc.comps["preheater"], "in1", label="22")
        c27 = Connection(orc.comps["preheater"], "out1", geo_sink, "in1", label="27")

        self.nw.add_conns(c11, c12, c21, c22, c27)

        # component specifications
        orc.comps["condenser"].set_attr(pr1=1, pr2=0.98)
        orc.comps["evaporator"].set_attr(pr1=0.98)
        orc.comps["preheater"].set_attr(pr1=0.98, pr2=0.98)
        orc.comps["valve"].set_attr(pr=1, design=['pr'])

        # connection specifications

        # orc cycle fluid
        orc.conns["0"].set_attr(fluid={working_fluid: 1, "water": 0})
        # turbine inlet temperature
        orc.conns["6"].set_attr(T=geo_temperature - 15, design=["T"])

        c11.set_attr(
            fluid={working_fluid: 0, "water": 1},
            T=self.T0,
            p=self.p0
        )

        c12.set_attr(T=self.T0 + 10)

        c21.set_attr(
            fluid={working_fluid: 0, "water": 1},
            T=geo_temperature,
            p=geo_pressure,
            m=geo_mass_flow,
        )

        # return steam mass fraction drum
        orc.conns["5"].set_attr(x=0.5)

        # these specifications are for stable starting values
        orc.conns["2"].set_attr(h=Ref(orc.conns["1"], 1, 5))
        orc.conns["8"].set_attr(h=Ref(orc.conns["7"], 1, -100))
        # geobrine temperature between evaporator and preheater
        c22.set_attr(T=90)
        # condensing pressure
        orc.conns["0"].set_attr(
            p=PropsSI(
                "P", "Q", 1, "T", 273.15 + self.T0 + 15, working_fluid
            )
            / 1e5
        )
        # steam mass fraction after preheating
        orc.conns["3"].set_attr(x=0)

        self.nw.solve("design")
        self.stable = working_fluid + "_stable"
        self.nw.save(self.stable)

        orc.conns["2"].set_attr(h=None)
        orc.conns["8"].set_attr(h=None)
        orc.comps["turbine"].set_attr(eta_s=0.9, design=['eta_s'], offdesign=['eta_s_char', 'cone'])
        orc.comps["feed pump"].set_attr(eta_s=0.75, design=['eta_s'], offdesign=['eta_s_char'])

        c22.set_attr(T=None)
        orc.comps["evaporator"].set_attr(ttd_l=10, design=['ttd_l'], offdesign=['kA_char'])
        orc.conns["0"].set_attr(p=None)
        orc.comps["condenser"].set_attr(ttd_u=10, design=['ttd_u'], offdesign=['kA_char'])
        orc.comps["preheater"].set_attr(offdesign=['kA_char'])
        orc.conns["3"].set_attr(x=None, Td_bp=-3, design=['Td_bp'])

        self.power_bus = Bus('power output')
        self.heat_bus = Bus('heat output')
        self.power_bus.add_comps(
            {'comp': orc.comps["turbine"], 'char': 0.97},
            {'comp': orc.comps["feed pump"], 'base': 'bus', 'char': 0.97}
        )
        self.nw.add_busses(self.power_bus, self.heat_bus)

        self.nw.solve("design")

    def solve_model(self, **kwargs):
        self.solve_design(**kwargs)

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

    def get_param(self, obj, label, parameter):
        return self.get_single_parameter(obj, label, parameter)

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

    def solve_design(self, **kwargs):

        self.set_parameters(**kwargs)

        self.solved = False
        try:
            self.nw.solve("design", max_iter=15)
            if self.nw.res[-1] >= 1e-3 or self.nw.lin_dep:
                self.nw.solve("design", init_only=True, init_path=self.stable)
            else:
                if any(self.nw.results['HeatExchanger']['Q'] > 0):
                    self.solved = False
                else:
                    self.solved = True
        except ValueError as e:
            print(e)
            self.nw.lin_dep = True
            self.nw.solve("design", init_only=True, init_path=self.stable)

    def solve_offdesign(self, init_path=None, **kwargs):

        self.set_parameters(**kwargs)

        self.solved = False
        try:
            if init_path is None:
                self.nw.solve("offdesign", design_path=self.design_path)
            else:
                self.nw.solve("offdesign", design_path=self.design_path, init_path=init_path)
            if self.nw.res[-1] >= 1e-3 or self.nw.lin_dep:
                self.nw.solve(
                    "offdesign", init_only=True, init_path=self.design_path,
                    design_path=self.design_path
                )
            else:
                if any(self.nw.results['HeatExchanger']['Q'] > 0):
                    self.solved = False
                else:
                    self.solved = True
        except ValueError as e:
            print(e)
            print("The iteration failed with the following exception: " + e)
            self.nw.lin_dep = True
            self.nw.solve(
                "offdesign", init_only=True, init_path=self.design_path,
                design_path=self.design_path
            )

    def get_objective(self, label):
        if self.solved:
            if label == "net power":
                return self.power_bus.P.val
            elif label == "gross power":
                return
            elif label == "heat":
                return
            else:
                return
        else:
            return np.nan

    def insert_dh_and_cw(self):

        # district heating system
        dh_return_temperature = 35
        dh_feed_temperature = 55
        dh_pressure = 2

        # components
        geo_splitter = Splitter("geo splitter")
        geo_merge = Merge("geo merge")
        geo_reinjection = self.nw.get_comp("geo re-injection")

        # pump for district heating system?
        dh_source = Source("dh return")
        dh_sink = Sink("dh feed")
        dh_heat_exchanger = HeatExchanger("dh heat exchanger")

        # cooling water system
        lw_source = Source("lw source")
        lw_sink = Sink("lw sink")
        lw_pump = Pump("lw pump")

        self.nw.del_conns(*self.nw.get_conn(["11", "12", "22", "27"]))

        # cooling water system
        c11 = Connection(
            lw_source, "out1", lw_pump, "in1", label="11"
        )
        c12 = Connection(
            lw_pump, "out1", self.nw.get_comp("condenser"), "in2", label="12"
        )
        c13 = Connection(
            self.nw.get_comp("condenser"), "out2", lw_sink, "in1", label="13"
        )
        self.nw.add_conns(c11, c12, c13)

        # geo feed
        c22 = Connection(self.nw.get_comp("evaporator"), "out1", geo_splitter, "in1", label="22")

        # district heating
        c23 = Connection(geo_splitter, "out1", dh_heat_exchanger, "in1", label="23")
        c24 = Connection(dh_heat_exchanger, "out1", geo_merge, "in1", label="24")

        # orc
        c25 = Connection(geo_splitter, "out2", self.nw.get_comp("preheater"), "in1", label="25")
        c26 = Connection(self.nw.get_comp("preheater"), "out1", geo_merge, "in2", label="26")

        c27 = Connection(
            geo_merge, "out1", geo_reinjection, "in1", label="27"
        )
        self.nw.add_conns(c22, c23, c24, c25, c26, c27)

        # district heating
        c31 = Connection(dh_source, "out1", dh_heat_exchanger, "in2", label="31")
        c32 = Connection(dh_heat_exchanger, "out2", dh_sink, "in1", label="32")

        self.nw.add_conns(c31, c32)

        # no pr1 required, parallel to preheater
        dh_heat_exchanger.set_attr(pr2=0.98, offdesign=['kA_char'])
        c31.set_attr(
            fluid={self.working_fluid: 0, "water": 1}, T=dh_return_temperature,
            p=dh_pressure
        )
        c32.set_attr(T=dh_feed_temperature)

        # brine temperature after dh heat exchanger
        c24.set_attr(T=90)
        c26.set_attr(T=90)
        self.nw.get_conn("6").set_attr(T=105)


        lw_pump.set_attr(eta_s=0.75, design=['eta_s'], offdesign=['eta_s_char'])

        c11.set_attr(
            fluid={self.working_fluid: 0, "water": 1},
            T=self.T0,
            p=self.p0
        )

        c13.set_attr(T=self.T0 + 10, p=self.p0)


        self.power_bus.add_comps(
            {'comp': lw_pump, 'base': 'bus', 'char': 0.97}
        )

        self.heat_bus.add_comps(
            {'comp': dh_heat_exchanger}
        )

        # solve the network
        self.nw.solve("design")
