import numpy as np

from CoolProp.CoolProp import PropsSI
from tespy.components import (
    Condenser,
    CycleCloser,
    Drum,
    HeatExchanger,
    Pump,
    Sink,
    Source,
    Turbine,
)
from tespy.components.subsystem import Subsystem
from tespy.connections import Connection, Ref
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
        self.comps["turbine"] = Turbine("turbine")
        self.comps["orc cycle closer"] = CycleCloser("orc cycle closer")

        # cooling water system
        self.comps["lw source"] = Source("lw source")
        self.comps["lw sink"] = Sink("lw sink")
        self.comps["lw pump"] = Pump("lw pump")

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
            self.comps["drum"], "out2", self.comps["turbine"], "in1", label="6"
        )
        self.conns["7"] = Connection(
            self.comps["turbine"], "out1", self.comps["condenser"], "in1", label="7"
        )

        # cooling water system
        self.conns["11"] = Connection(
            self.comps["lw source"], "out1", self.comps["lw pump"], "in1", label="11"
        )
        self.conns["12"] = Connection(
            self.comps["lw pump"], "out1", self.comps["condenser"], "in2", label="12"
        )
        self.conns["13"] = Connection(
            self.comps["condenser"], "out2", self.comps["lw sink"], "in1", label="13"
        )


class ORC_with_ihe(Subsystem):
    def create_comps(self):
        """Create the subsystem's components."""

        # main cycle
        self.comps["condenser"] = Condenser("condenser")
        self.comps["feed pump"] = Pump("feed pump")
        self.comps["preheater"] = HeatExchanger("preheater")
        self.comps["evaporator"] = HeatExchanger("evaporator")
        self.comps["drum"] = Drum("drum")
        self.comps["turbine"] = Turbine("turbine")
        self.comps["orc cycle closer"] = CycleCloser("orc cycle closer")
        # internal heat exchanger
        self.comps["ihe"] = HeatExchanger("ihe")

        # cooling water system
        self.comps["lw source"] = Source("lw source")
        self.comps["lw sink"] = Sink("lw sink")
        self.comps["lw pump"] = Pump("lw pump")

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
        self.conns["2_1"] = Connection(
            self.comps["feed pump"], "out1", self.comps["ihe"], "in2", label="2_1"
        )
        self.conns["2_2"] = Connection(
            self.comps["ihe"], "out1", self.comps["preheater"], "in2", label="2_2"
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
            self.comps["drum"], "out2", self.comps["turbine"], "in1", label="6"
        )
        self.conns["7_1"] = Connection(
            self.comps["turbine"], "out1", self.comps["ihe"], "in1", label="7_1"
        )
        self.conns["7_2"] = Connection(
            self.comps["ihe"], "out1", self.comps["condenser"], "in1", label="7_2"
        )

        # cooling water system
        self.conns["11"] = Connection(
            self.comps["lw source"], "out1", self.comps["lw pump"], "in1", label="11"
        )
        self.conns["12"] = Connection(
            self.comps["lw pump"], "out1", self.comps["condenser"], "in2", label="12"
        )
        self.conns["13"] = Connection(
            self.comps["condenser"], "out2", self.comps["lw sink"], "in1", label="13"
        )


class CHPORC:
    def __init__(self, working_fluid):

        self.working_fluid = working_fluid
        fluids = ["water", working_fluid]
        self.nw = Network(fluids=fluids)
        self.nw.set_attr(p_unit="bar", T_unit="C", h_unit="kJ / kg", iterinfo=False)

        # geo parameters
        geo_mass_flow = 10
        geo_temperature = 100
        geo_pressure = 25

        # lake water parameters & exergy analysis if required
        ambient_temperature = 15
        ambient_pressure = 1

        orc = ORC_without_ihe("orc")
        self.nw.add_subsys(orc)

        # pump for geo water?
        geo_source = Source("geo source")
        geo_sink = Sink("geo re-injection")

        # Connections

        # ORC only for stable starting values
        c21 = Connection(geo_source, "out1", orc.comps["evaporator"], "in1", label="21")
        c22 = Connection(
            orc.comps["evaporator"], "out1", orc.comps["preheater"], "in1", label="22"
        )
        c27 = Connection(orc.comps["preheater"], "out1", geo_sink, "in1", label="27")

        self.nw.add_conns(c21, c22, c27)

        # component specifications
        orc.comps["condenser"].set_attr(pr1=1, pr2=0.98)
        orc.comps["evaporator"].set_attr(pr1=0.98)
        orc.comps["preheater"].set_attr(pr1=0.98, pr2=0.98)

        # connection specifications

        # orc cycle fluid
        orc.conns["0"].set_attr(fluid={working_fluid: 1, "water": 0})
        # turbine inlet temperature
        orc.conns["6"].set_attr(T=90)

        # cooling water
        orc.conns["11"].set_attr(
            fluid={working_fluid: 0, "water": 1},
            T=ambient_temperature,
            p=ambient_pressure,
        )
        orc.conns["13"].set_attr(T=ambient_temperature + 10, p=ambient_pressure)
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
        orc.conns["12"].set_attr(h=Ref(orc.conns["11"], 1, 5))
        orc.conns["7"].set_attr(h=Ref(orc.conns["6"], 1, -100))
        # geobrine temperature between evaporator and preheater
        c22.set_attr(T=90)
        # condensing pressure
        orc.conns["0"].set_attr(
            p=PropsSI(
                "P", "Q", 1, "T", 273.15 + ambient_temperature + 15, working_fluid
            )
            / 1e5
        )
        # steam mass fraction after preheating
        orc.conns["3"].set_attr(x=0)

        self.nw.solve("design")
        self.stable = working_fluid + "_stable"
        self.nw.save(self.stable)

        orc.conns["2"].set_attr(h=None)
        orc.conns["12"].set_attr(h=None)
        orc.conns["7"].set_attr(h=None)
        orc.comps["turbine"].set_attr(eta_s=0.9)
        orc.comps["feed pump"].set_attr(eta_s=0.75)
        orc.comps["lw pump"].set_attr(eta_s=0.75)

        c22.set_attr(T=None)
        orc.comps["evaporator"].set_attr(ttd_l=5)
        orc.conns["0"].set_attr(p=None)
        orc.comps["condenser"].set_attr(ttd_u=5)
        orc.conns["3"].set_attr(x=None, Td_bp=-3)

    def get_param(self, obj, label, parameter):
        if obj == 'Components':
            return self.nw.get_comp(label).get_attr(parameter).val
        elif obj == 'Connections':
            return self.nw.get_conn(label).get_attr(parameter).val

    def set_params(self, **kwargs):

        if "Connections" in kwargs:
            for c, params in kwargs["Connections"].items():
                self.nw.get_conn(c).set_attr(**params)

        if "Components" in kwargs:
            for c, params in kwargs["Components"].items():
                self.nw.get_comp(c).set_attr(**params)

    def solve_model(self, **kwargs):

        self.set_params(**kwargs)

        self.solved = False
        try:
            self.nw.solve("design")
            if self.nw.res[-1] >= 1e-3 or self.nw.lin_dep:
                self.nw.solve("design", init_only=True, init_path=self.stable)
            else:
                self.solved = True
        except:
            self.nw.lin_dep = True
            self.nw.solve("design", init_only=True, init_path=self.stable)

    def get_objective(self, label):
        if self.solved:
            if label == "net power":
                return self.nw.get_comp('turbine').P.val + self.nw.get_comp('lw pump').P.val + self.nw.get_comp('feed pump').P.val
            elif label == "gross power":
                return
            elif label == "heat":
                return
            else:
                return
        else:
            return np.nan
