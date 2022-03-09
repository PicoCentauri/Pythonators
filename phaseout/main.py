# -*- coding: utf-8 -*-
"""
Created on Sat Mar  5 16:34:07 2022

@author: moham
"""

import numpy as np
import pandas as pd  # import pandas to work with dataframes

import pv_wind_storage
import gas
import nuclear

# %%
capacityFactors = pd.read_csv(
    'input/renewable_cf2019.csv', index_col=0, parse_dates=True)
other_ren_gen = pd.read_csv(
    'input/2020_other_ren_gen_1h.csv', index_col=0, parse_dates=True)

# Demand data for 2030 (source: nat. comm. paper)
data = pd.read_csv('input/demand_2030.csv', index_col=0,
                   parse_dates=True)  # in MWh

# Capacities for 2022 (source: energy charts)
installedSolarCapacity = 59400  # MW
installedOnWindCapacity = 56510  # MW
installedOffWindCapacity = 7770  # MW
installedGasCapacity = 31680  # MW

# %% Costs for 2030 (source: nat. comm. paper table 4)
solarCost = 254e-3  # mln EUR per MW installed capacity
windOnshoreCost = 1035e-3  # mln EUR per MW installed capacity
windOffshoreCost = 1934e-3  # mln EUR per MW installed capacity
storageCost = 142e-3  # mln EUR per MWh installed capacity

chargingEfficiency = 0.82
dischargingEfficiency = 0.92
initialSOC = 0.5  # initial State of Charge (ratio from capacity)

# %% Run Scenario 1 (PV, Wind, Storage)
pv_wind_storage.run(data=data,
                    capacityFactors=capacityFactors,
                    renewableShareTarget=0.8,
                    installedSolarCapacity=installedSolarCapacity,
                    installedOnWindCapacity=installedOnWindCapacity,
                    installedOffWindCapacity=installedOffWindCapacity,
                    other_ren_gen=other_ren_gen,
                    installedStorageCapacity=1.22e3,  # in MWh
                    storagePower=0.42e3,  # in MW
                    initialSOC=initialSOC,
                    chargingEfficiency=chargingEfficiency,
                    dischargingEfficiency=dischargingEfficiency,
                    solarCost=solarCost,
                    windOnshoreCost=windOnshoreCost,
                    windOffshoreCost=windOffshoreCost,
                    storageCost=storageCost)

# %% Run Scenario 2 (Gas)
gas.run(data=data,
        capacityFactors=capacityFactors,
        renewableShareTarget=0.8,
        installedSolarCapacity=installedSolarCapacity,
        installedOnWindCapacity=installedOnWindCapacity,
        installedOffWindCapacity=installedOffWindCapacity,
        installedGasCapacity=installedGasCapacity,
        other_ren_gen=other_ren_gen,
        installedStorageCapacity=1.22e3,  # in MWh
        storagePower=0.42e3,  # in MW
        initialSOC=initialSOC,
        chargingEfficiency=chargingEfficiency,
        dischargingEfficiency=dischargingEfficiency,
        solarCost=solarCost,
        windOnshoreCost=windOnshoreCost,
        windOffshoreCost=windOffshoreCost,
        storageCost=storageCost)

# %% Run Scenario 3 (Nuclear 2010)
nuclear.run(data=data,
        capacityFactors=capacityFactors,
        renewableShareTarget=0.8,
        installedSolarCapacity=installedSolarCapacity,
        installedOnWindCapacity=installedOnWindCapacity,
        installedOffWindCapacity=installedOffWindCapacity,
        installedNuclearCapacity=21.5e3,  # in MW (source: energycharts)
        other_ren_gen=other_ren_gen,
        installedStorageCapacity=1.22e3,  # in MWh
        storagePower=0.42e3,  # in MW
        initialSOC=initialSOC,
        chargingEfficiency=chargingEfficiency,
        dischargingEfficiency=dischargingEfficiency,
        solarCost=solarCost,
        windOnshoreCost=windOnshoreCost,
        windOffshoreCost=windOffshoreCost,
        storageCost=storageCost)

# %% Run Scenario 4 (Nuclear 2016)
nuclear.run(data=data,
        capacityFactors=capacityFactors,
        renewableShareTarget=0.8,
        installedSolarCapacity=installedSolarCapacity,
        installedOnWindCapacity=installedOnWindCapacity,
        installedOffWindCapacity=installedOffWindCapacity,
        installedNuclearCapacity=10.8e3,  # in MW (source: energycharts)
        other_ren_gen=other_ren_gen,
        installedStorageCapacity=1.22e3,  # in MWh
        storagePower=0.42e3,  # in MW
        initialSOC=initialSOC,
        chargingEfficiency=chargingEfficiency,
        dischargingEfficiency=dischargingEfficiency,
        solarCost=solarCost,
        windOnshoreCost=windOnshoreCost,
        windOffshoreCost=windOffshoreCost,
        storageCost=storageCost)