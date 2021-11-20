from tespy.connections import Connection
from tespy.components import (
    HeatExchanger, Pump, Turbine, Source, Sink, CycleCloser,
    Condenser, Drum
)
from tespy.components.subsystem import Subsystem

class ORC_without_ihe(Subsystem):

    def create_comps(self):
        """Create the subsystem's components."""

        # main cycle
        self.comps['condenser'] = Condenser('condenser')
        self.comps['feed pump'] = Pump('feed pump')
        self.comps['preheater'] = HeatExchanger('preheater')
        self.comps['evaporator'] = HeatExchanger('evaporator')
        self.comps['drum'] = Drum('drum')
        self.comps['turbine'] = Turbine('turbine')
        self.comps['orc cycle closer'] = CycleCloser('orc cycle closer')

        # cooling water system
        self.comps['lw source'] = Source('lw source')
        self.comps['lw sink'] = Sink('lw sink')
        self.comps['lw pump'] = Pump('lw pump')

    def create_conns(self):
        """Define the subsystem's connections."""

        # main cycle
        self.conns['0'] = Connection(
            self.comps['condenser'], 'out1',
            self.comps['orc cycle closer'], 'in1', label='0'
        )
        self.conns['1'] = Connection(
            self.comps['orc cycle closer'], 'out1',
            self.comps['feed pump'], 'in1', label='1'
        )
        self.conns['2'] = Connection(
            self.comps['feed pump'], 'out1',
            self.comps['preheater'], 'in2', label='2'
        )
        self.conns['3'] = Connection(
            self.comps['preheater'], 'out2',
            self.comps['drum'], 'in1', label='3'
        )
        self.conns['4'] = Connection(
            self.comps['drum'], 'out1',
            self.comps['evaporator'], 'in2', label='4'
        )
        self.conns['5'] = Connection(
            self.comps['evaporator'], 'out2',
            self.comps['drum'], 'in2', label='5'
        )
        self.conns['6'] = Connection(
            self.comps['drum'], 'out2',
            self.comps['turbine'], 'in1', label='6'
        )
        self.conns['7'] = Connection(
            self.comps['turbine'], 'out1',
            self.comps['condenser'], 'in1', label='7'
        )

        # cooling water system
        self.conns['11'] = Connection(
            self.comps['lw source'], 'out1',
            self.comps['lw pump'], 'in1', label='11'
        )
        self.conns['12'] = Connection(
            self.comps['lw pump'], 'out1',
            self.comps['condenser'], 'in2', label='12'
        )
        self.conns['13'] = Connection(
            self.comps['condenser'], 'out2',
            self.comps['lw sink'], 'in1', label='13'
        )


class ORC_with_ihe(Subsystem):

    def create_comps(self):
        """Create the subsystem's components."""

        # main cycle
        self.comps['condenser'] = Condenser('condenser')
        self.comps['feed pump'] = Pump('feed pump')
        self.comps['preheater'] = HeatExchanger('preheater')
        self.comps['evaporator'] = HeatExchanger('evaporator')
        self.comps['drum'] = Drum('drum')
        self.comps['turbine'] = Turbine('turbine')
        self.comps['orc cycle closer'] = CycleCloser('orc cycle closer')
        # internal heat exchanger
        self.comps['ihe'] = HeatExchanger('ihe')

        # cooling water system
        self.comps['lw source'] = Source('lw source')
        self.comps['lw sink'] = Sink('lw sink')
        self.comps['lw pump'] = Pump('lw pump')

    def create_conns(self):
        """Define the subsystem's connections."""

        # main cycle
        self.conns['0'] = Connection(
            self.comps['condenser'], 'out1',
            self.comps['orc cycle closer'], 'in1', label='0'
        )
        self.conns['1'] = Connection(
            self.comps['orc cycle closer'], 'out1',
            self.comps['feed pump'], 'in1', label='1'
        )
        self.conns['2_1'] = Connection(
            self.comps['feed pump'], 'out1',
            self.comps['ihe'], 'in2', label='2_1'
        )
        self.conns['2_2'] = Connection(
            self.comps['ihe'], 'out1',
            self.comps['preheater'], 'in2', label='2_2'
        )
        self.conns['3'] = Connection(
            self.comps['preheater'], 'out2',
            self.comps['drum'], 'in1', label='3'
        )
        self.conns['4'] = Connection(
            self.comps['drum'], 'out1',
            self.comps['evaporator'], 'in2', label='4'
        )
        self.conns['5'] = Connection(
            self.comps['evaporator'], 'out2',
            self.comps['drum'], 'in2', label='5'
        )
        self.conns['6'] = Connection(
            self.comps['drum'], 'out2',
            self.comps['turbine'], 'in1', label='6'
        )
        self.conns['7_1'] = Connection(
            self.comps['turbine'], 'out1',
            self.comps['ihe'], 'in1', label='7_1'
        )
        self.conns['7_2'] = Connection(
            self.comps['ihe'], 'out1',
            self.comps['condenser'], 'in1', label='7_2'
        )

        # cooling water system
        self.conns['11'] = Connection(
            self.comps['lw source'], 'out1',
            self.comps['lw pump'], 'in1', label='11'
        )
        self.conns['12'] = Connection(
            self.comps['lw pump'], 'out1',
            self.comps['condenser'], 'in2', label='12'
        )
        self.conns['13'] = Connection(
            self.comps['condenser'], 'out2',
            self.comps['lw sink'], 'in1', label='13'
        )
