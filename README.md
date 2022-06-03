# Geothermal ORC combined heat and power plant for New Town

Application of [TESPy][] for a combined heat and power ORC using a geothermal
high temperature heat source. This repository only contains the geothermal ORC
simulation models, the district heat system itself is not simulated.

## Model description

A time series of geothermal production temperature for different geothermal
mass flows, i.e. 30 kg/s, 40 kg/s and 50 kg/s, is provided in quarterly data,
assuming constant geothermal production for three months.

The simulation model calculates the power output of the geothermal ORC
following a heat demand curve. For that, the maximum monthly heat demand is
mapped to the design heat production of the plant and the heat production for
the other months is scaled respectively.

Two different variants - a high temperature district heating system and a low
temperature district heating system - are available. The waste heat from the
ORC is discharged into the lake in the high temperature district heating system.
In the low temperature variant only surplus heat, that cannot be taken by the
district heating system is discharged into the lake.

## Plant layouts

For the high temperature district heating system the ORC provides heat at 55 °C
assuming a return temperature of 35 °C. The ORC plant has the following
topology as suggested in LINKTOORIGINALSTUDIES.

<figure>
<img src="./flowsheet_dh_high_T.svg" class="align-center" />
</figure>

In the low temperature district heating system heat is provided at 30 °C, which
is then increased locally using decentral heat pumps. The ORC uses the district
heating system as heat sink. The lake water can be used for cooling
simultanously, in case the district heating system cannot take the heat demand.

<figure>
<img src="./flowsheet_dh_low_T.svg" class="align-center" />
</figure>

## Usage

Clone the repository and build a new `python3.8` environment and install the
requirements to it.

``` bash
pip install -r ./requirements.txt
```

To run the simulation for the high temperature system run

``` bash
python run_ht_dh.py input/inputfile.json
```

and run

``` bash
python run_lt_dh.py input/inputfile.json
```

for the low temperature system.

Please exchange the "inputfile.json" with the respective scenario you want to
simulate, e.g. "high_temp_dh_1500.json". Currently, it is possibel to specify
the design geothermal temperature as well as the design heat production of the
plant.

**The tool is quite flexibile in parameter settings, if you want to learn more**
**on how to change parameters, please contact us.**

## Citation

The state of this repository is archived via zenodo. If you are using the
TESPy model within your own research, you can refer to this model via the
zenodo doi: [10.5281/zenodo.6592257][].

## MIT License

Copyright (c) 2022 Francesco Witte, Nicholas Fry

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


  [TESPy]: https://github.com/oemof/tespy
  [10.5281/zenodo.6592257]: https://zenodo.org/record/6592257
