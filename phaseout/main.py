# -*- coding: utf-8 -*-
"""

Python Project: Scenarios for 2030

Student 1 name: Mohamed Eltoukhy, 5170372
Student 2 name: Anna Lebowsky, 5143788

"""
import os

import numpy as np
import pandas as pd  # import pandas to work with dataframes

import pv_wind_storage
import gas
import nuclear2010
import nuclear2016

from plots import plot_demand

# %% Load Parameters

params = dict(
    # Demand data for 2030 (source: nat. comm. paper)
    data = pd.read_csv('input/demand_2030.csv', index_col=0,
                    parse_dates=True),  # in MWh
    capacityFactors = pd.read_csv('input/renewable_cf2019.csv',
                                  index_col=0,
                                  parse_dates=True),
    other_ren_gen = pd.read_csv('input/2019_other_ren_gen.csv',
                                index_col=0,
                                parse_dates=True),  # smard.de
    # Capacities for 2022 (source: energy charts)
    installedSolarCapacity = 59400,  # MW
    installedOnWindCapacity = 56510,  # MW
    installedOffWindCapacity = 7770,  # MW
    #Costs for 2030 (source: nat. comm. paper table 4)
    solarCost = 254e-3,  # mln EUR per MW installed capacity
    windOnshoreCost = 1035e-3,  # mln EUR per MW installed capacity
    windOffshoreCost = 1934e-3,  # mln EUR per MW installed capacity
    storageCost = 142e-3,  # mln EUR per MWh installed capacity
    chargingEfficiency = 0.82,
    dischargingEfficiency = 0.92,
    initialSOC = 0.5,  # initial State of Charge (ratio from capacity)
    installedStorageCapacity=46.35e3,  # in MWh energycharts 2022
    storagePower=10.38e3,  # in MW energycharts 2022
    renewableShareTarget=0.85,
)

# %%
print("-- Run Scenario 1 (PV, Wind, Storage) --")
pv_wind_storage.run(**params)

# %%
print("-- Run Scenario 2 (Gas) --")

params["renewableShareTarget"] = 0.8
params["installedGasCapacity"] = 31680  # MW
params["gasCost"] = 560-3  # MW
gas.run(**params)

# %% 
print("-- Run Scenario 3 (Nuclear 2010) --")
nuclear2010.run(**params)

# %%
print("-- Run Scenario 4 (Nuclear 2016) --")
nuclear2016.run(**params)

#%% Plot results

# create output folder
try:
    os.mkdir("output")
except OSError:
    # Ignore raised error if folder already exists
    pass

plot_demand(data=params["data"])
