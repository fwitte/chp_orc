from tespy.components.heat_exchangers.condenser import Condenser
from tespy.connections import Connection, Bus, Ref
from tespy.networks import Network
from tespy.components import (
    HeatExchanger, Pump, Source, Sink, Splitter, Merge
)
from orc import ORC_without_ihe
from CoolProp.CoolProp import PropsSI


working_fluid = 'Isopentane'
fluids = ['water', working_fluid]
nw = Network(fluids=fluids)
nw.set_attr(p_unit='bar', T_unit='C', h_unit='kJ / kg')

# geo parameters
geo_mass_flow = 1
geo_temperature = 100
geo_pressure = 25

# lake water parameters & exergy analysis if required
ambient_temperature = 15
ambient_pressure = 1

# district heating system
dh_return_temperature = 60
dh_feed_temperature = 40
dh_pressure = 5

orc = ORC_without_ihe('orc')
nw.add_subsys(orc)

# pump for geo water?
geo_source = Source('geo source')
geo_sink = Sink('geo re-injection')
geo_sink1 = Sink('geo re-injection 1')
geo_sink2 = Sink('geo re-injection 2')
geo_splitter = Splitter('geo splitter')
geo_merge = Merge('geo merge')

# pump for district heating system?
dh_source = Source('dh return')
dh_sink = Sink('dh feed')
dh_heat_exchanger = HeatExchanger('dh heat exchanger')

# Connections

c21 = Connection(geo_source, 'out1', orc.comps['evaporator'], 'in1', label='21')
# c22 = Connection(orc.comps['evaporator'], 'out1', geo_splitter, 'in1', label='22')
c22 = Connection(orc.comps['evaporator'], 'out1', orc.comps['preheater'], 'in1', label='22')

# district heating
# c23 = Connection(geo_splitter, 'out1', dh_heat_exchanger, 'in1', label='23')
# c24 = Connection(dh_heat_exchanger, 'out1', geo_merge, 'in1', label='24')

# orc
# c25 = Connection(geo_splitter, 'out2', orc.comps['preheater'], 'in1', label='25')
# c26 = Connection(orc.comps['preheater'], 'out1', geo_merge, 'in2', label='26')

# c27 = Connection(geo_merge, 'out1', geo_sink, 'in1', label='27')
c27 = Connection(orc.comps['preheater'], 'out1', geo_sink, 'in1', label='27')

nw.add_conns(c21, c22, c27) #c23, c24, c25, c26, c27)

# district heating
# c31= Connection(dh_source, 'out1', dh_heat_exchanger, 'in2', label='31')
# c32 = Connection(dh_heat_exchanger, 'out2', dh_sink, 'in1', label='32')

# nw.add_conns(c31, c32)

# component specifications
orc.comps['condenser'].set_attr(pr1=1, pr2=0.98)
orc.comps['evaporator'].set_attr(pr1=0.98)
orc.comps['preheater'].set_attr(pr1=0.98, pr2=0.98, ttd_u=10)
orc.comps['turbine'].set_attr(eta_s=0.9)
orc.comps['feed pump'].set_attr(eta_s=0.75)
orc.comps['lw pump'].set_attr(eta_s=0.75)
# no pr1 required, parallel to preheater
dh_heat_exchanger.set_attr(pr2=0.98)#, ttd_u=10)

# connection specifications
orc.conns['0'].set_attr(fluid={working_fluid: 1, 'water': 0}, T=30)
orc.conns['11'].set_attr(fluid={working_fluid: 0, 'water': 1}, T=ambient_temperature, p=ambient_pressure)
# lake feed in temperature, pressure equal to inlet
orc.conns['13'].set_attr(T=ambient_temperature + 10, p=ambient_pressure)
c21.set_attr(fluid={working_fluid: 0, 'water': 1}, T=geo_temperature, p=geo_pressure, m=geo_mass_flow)
c22.set_attr(fluid0={working_fluid: 0, 'water': 1})
# c23.set_attr(fluid0={working_fluid: 0, 'water': 1})
# c24.set_attr(fluid0={working_fluid: 0, 'water': 1})
c27.set_attr(fluid0={working_fluid: 0, 'water': 1})
# c31.set_attr(fluid={working_fluid: 0, 'water': 1}, T=dh_feed_temperature, p=dh_pressure)
# c32.set_attr(T=dh_return_temperature)
# for stable start: set turbine inlet temperature/pressure
orc.conns['6'].set_attr(T=90)#p=PropsSI('P', 'Q', 1, 'T', 273.15 + 90, working_fluid) / 1e5, h0=PropsSI('H', 'Q', 1, 'T', 273.15 + 90, working_fluid) / 1e3)
orc.conns['7'].set_attr()
# split geobrine stream 50/50
# c23.set_attr(m=Ref(c22, .5, 0))
# approach point temperature difference
orc.conns['3'].set_attr(x=0)
# return steam mass fraction drum
orc.conns['5'].set_attr(x=.8)

# drum circulation, terminal temperature differences, ..? 8 more required!
# splitting mass flow

nw.solve('design')

orc.conns['3'].set_attr(x=None, Td_bp=-3)
orc.conns['0'].set_attr(T=None)
orc.comps['condenser'].set_attr(ttd_u=5)

nw.solve('design')

nw.del_conns(c22, c27)

c22 = Connection(orc.comps['evaporator'], 'out1', geo_splitter, 'in1', label='22')

# district heating
c23 = Connection(geo_splitter, 'out1', dh_heat_exchanger, 'in1', label='23')
c24 = Connection(dh_heat_exchanger, 'out1', geo_merge, 'in1', label='24')

# orc
c25 = Connection(geo_splitter, 'out2', orc.comps['preheater'], 'in1', label='25')
c26 = Connection(orc.comps['preheater'], 'out1', geo_merge, 'in2', label='26')

c27 = Connection(geo_merge, 'out1', geo_sink1, 'in1', label='27')
nw.add_conns(c22, c23, c24, c25, c26, c27)

# district heating
c31= Connection(dh_source, 'out1', dh_heat_exchanger, 'in2', label='31')
c32 = Connection(dh_heat_exchanger, 'out2', dh_sink, 'in1', label='32')

nw.add_conns(c31, c32)

c24.set_attr(T=50)
c31.set_attr(fluid={working_fluid: 0, 'water': 1}, T=dh_feed_temperature, p=dh_pressure, m=1)
c32.set_attr(T=dh_return_temperature)

nw.solve('design')
nw.print_results()