# -*- coding: utf-8 -*-
"""

Python Project: Scenarios for 2030

Student 1 name: Mohamed Eltoukhy, 5170372
Student 2 name: Anna Lebowsky, 5143788

"""
import os

import pandas as pd

import pv_wind_storage
import gas
import nuclear

from plots import plot_demand, plot_investments

# %% Load Parameters

# Hour step for the optimization. Increase for sparse the data for faster 
# optimization. For DH=1 the whole data is taken into account
DH = 100

params = dict(
    # Demand data for 2030 (source: nat. comm. paper)
    data=pd.read_csv('input/demand_2030.csv', index_col=0,
                     parse_dates=True)[::DH],  # in MWh
    capacityFactors=pd.read_csv('input/renewable_cf2019.csv',
                                index_col=0,
                                parse_dates=True)[::DH],
    other_ren_gen=pd.read_csv('input/2019_other_ren_gen.csv',
                              index_col=0,
                              parse_dates=True)[::DH],  # smard.de
    # Capacities for 2022 (source: energy charts)
    installedSolarCapacity=59400,  # MW
    installedOnWindCapacity=56510,  # MW
    installedOffWindCapacity=7770,  # MW
    #Costs for 2030 (source: nat. comm. paper table 4)
    solarCost=254e-3,  # mln EUR per MW installed capacity
    windOnshoreCost=1035e-3,  # mln EUR per MW installed capacity
    windOffshoreCost=1934e-3,  # mln EUR per MW installed capacity
    storageCost=142e-3,  # mln EUR per MWh installed capacity
    chargingEfficiency=0.82,
    dischargingEfficiency=0.92,
    initialSOC=0.5,  # initial State of Charge (ratio from capacity)
    installedStorageCapacity=46.35e3,  # in MWh energycharts 2022
    storagePower=10.38e3,  # in MW energycharts 2022
    renewableShareTarget=0.85,
)

# List of names for the different scenarios.
# Used for labelling output and plots
scenario_names = []

# %%
scenario_names.append("PV, Wind, Storage")
print(f"-- Run Scenario {len(scenario_names)} ({scenario_names[-1]}) --")
investment_pv_wind = pv_wind_storage.run(**params)

# %%
scenario_names.append("Gas")
print(f"-- Run Scenario {len(scenario_names)} ({scenario_names[-1]}) --")

params["renewableShareTarget"] = 0.8
params["installedGasCapacity"] = 31680  # MW
params["gasCost"] = 560 - 3  # MW
investment_gas = gas.run(**params)

# %%
scenario_names.append("Nuclear 2010")
print(f"-- Run Scenario {len(scenario_names)} ({scenario_names[-1]}) --")

params["nuclearGen_upper_bound"] = 21.5e3  # in MWh
investment_nuclear2010 = nuclear.run(**params)

# %%
# # Szenario 4 is currently broken and not runned!

# scenario_names.append("Nuclear 2016")
# print(f"-- Run Scenario {len(scenario_names)} ({scenario_names[-1]}) --")

# params["nuclearGen_upper_bound"] = 21.5e3 / 2  # in MWh
# investment_nuclear2016 = nuclear.run(**params)

#%% Plot results

# create output folder
try:
    os.mkdir("output")
except OSError:
    # Ignore raised error if folder already exists
    pass

plot_demand(data=params["data"])
plot_investments(scenario_names,
                 [investment_pv_wind, investment_gas, investment_nuclear2010])
