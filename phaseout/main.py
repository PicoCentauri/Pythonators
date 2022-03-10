# -*- coding: utf-8 -*-
"""

Python Project: Scenarios for 2030

Student 1 name: Mohamed Eltoukhy, 5170372
Student 2 name: Anna Lebowsky, 5143788

"""

import numpy as np
import pandas as pd  # import pandas to work with dataframes

import pv_wind_storage
import gas
import nuclear2010
import nuclear2016

from plots import plot_demand

# %%
capacityFactors = pd.read_csv(
    'input/renewable_cf2019.csv', index_col=0, parse_dates=True)
other_ren_gen = pd.read_csv(
    'input/2019_other_ren_gen.csv', index_col=0, parse_dates=True) # smard.de

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
gasCost = 560-3 # mln EUR per MW installed capacity

chargingEfficiency = 0.82
dischargingEfficiency = 0.92
initialSOC = 0.5  # initial State of Charge (ratio from capacity)

# %% Run Scenario 1 (PV, Wind, Storage)
# pv_wind_storage.run(data=data,
#                     capacityFactors=capacityFactors,
#                     renewableShareTarget=0.85,
#                     installedSolarCapacity=installedSolarCapacity,
#                     installedOnWindCapacity=installedOnWindCapacity,
#                     installedOffWindCapacity=installedOffWindCapacity,
#                     other_ren_gen=other_ren_gen,
#                     installedStorageCapacity=46.35e3,  # in MWh energycharts 2022
#                     storagePower=10.38e3,  # in MW energycharts 2022
#                     initialSOC=initialSOC,
#                     chargingEfficiency=chargingEfficiency,
#                     dischargingEfficiency=dischargingEfficiency,
#                     solarCost=solarCost,
#                     windOnshoreCost=windOnshoreCost,
#                     windOffshoreCost=windOffshoreCost,
#                     storageCost=storageCost)

# %% Run Scenario 2 (Gas)
# gas.run(data=data,
#         capacityFactors=capacityFactors,
#         renewableShareTarget=0.8,
#         installedSolarCapacity=installedSolarCapacity,
#         installedOnWindCapacity=installedOnWindCapacity,
#         installedOffWindCapacity=installedOffWindCapacity,
#         installedGasCapacity=installedGasCapacity,
#         other_ren_gen=other_ren_gen,
#         installedStorageCapacity=46.35e3,  # in MWh
#         storagePower=10.38e3,  # in MW
#         initialSOC=initialSOC,
#         chargingEfficiency=chargingEfficiency,
#         dischargingEfficiency=dischargingEfficiency,
#         solarCost=solarCost,
#         windOnshoreCost=windOnshoreCost,
#         windOffshoreCost=windOffshoreCost,
#         storageCost=storageCost,
#         gasCost=gasCost)

# %% Run Scenario 3 (Nuclear 2010)
# nuclear2010.run(data=data,
#         capacityFactors=capacityFactors,
#         renewableShareTarget=0.8,
#         installedSolarCapacity=installedSolarCapacity,
#         installedOnWindCapacity=installedOnWindCapacity,
#         installedOffWindCapacity=installedOffWindCapacity,
#         installedGasCapacity=installedGasCapacity,  # in MW (source: energycharts)
#         other_ren_gen=other_ren_gen,
#         installedStorageCapacity=46.35e3,  # in MWh
#         storagePower=10.38e3,  # in MW
#         initialSOC=initialSOC,
#         chargingEfficiency=chargingEfficiency,
#         dischargingEfficiency=dischargingEfficiency,
#         solarCost=solarCost,
#         windOnshoreCost=windOnshoreCost,
#         windOffshoreCost=windOffshoreCost,
#         storageCost=storageCost,
#         gasCost=gasCost)

# # %% Run Scenario 4 (Nuclear 2016)
nuclear2016.run(data=data,
        capacityFactors=capacityFactors,
        renewableShareTarget=0.8,
        installedSolarCapacity=installedSolarCapacity,
        installedOnWindCapacity=installedOnWindCapacity,
        installedOffWindCapacity=installedOffWindCapacity,
        installedGasCapacity=installedGasCapacity,  # in MW (source: energycharts)
        other_ren_gen=other_ren_gen,
        installedStorageCapacity=46.35e3,  # in MWh
        storagePower=10.38e3,  # in MW
        initialSOC=initialSOC,
        chargingEfficiency=chargingEfficiency,
        dischargingEfficiency=dischargingEfficiency,
        solarCost=solarCost,
        windOnshoreCost=windOnshoreCost,
        windOffshoreCost=windOffshoreCost,
        storageCost=storageCost,
        gasCost=gasCost)

#%%
# =============================================================================
# Plotting results
# =============================================================================

plot_demand(data=data)
