# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 08:55:45 2021

@author: intgrdnb-06

Global Input Data Module of the Merit Order Model
"""

import pandas as pd
import os
import matplotlib.pyplot as plt
# =============================================================================
# Defining the Working and Data Directory
# =============================================================================
# Setting of the Working and Data Directory using OS
workingDirectory = os.getcwd()
dataDirectory = f"{os.getcwd()}\data"


# =============================================================================
# Defining the Model Parameters and Boundaries and Importing the Input Data
# =============================================================================
# Demand in MWh given for each hour of the year 2019 for Germany
demandTimeSeries_2019 = pd.read_csv(f'{dataDirectory}/demand2019.csv', index_col=0, parse_dates = True)

# Demand in MWh given for each hour of the year 2030 for Germany
demandTimeSeries_2030 = pd.read_csv(f'{dataDirectory}/demand_2030.csv', index_col=0, parse_dates = True)

"""

***After comparing capacity factors of 2015, 2019 and 2020 we decided to keep 2019 because they were similar to 2015 and 2020 were to small (... for some reason)****

demandTimeSeries_2020 = pd.read_csv(f'{dataDirectory}/2020_demand_GER_1h.csv', index_col=0, parse_dates = True)

# Renewable capacity factors in percent for each hour of the year 2020 for Germany
cfTimeSeries_2020 = pd.read_csv(f'{dataDirectory}/2020_renewablesCF_GER_1h.csv', index_col=0, parse_dates = True)

# Renewable capacity factors in percent for each hour of the year 2015 for Germany
cfTimeSeries_2015 = pd.read_csv(f'{dataDirectory}/renewable_cf2015.csv', index_col=0, parse_dates = True)
"""
# Renewable capacity factors in percent for each hour of the year 2019 for Germany
cfTimeSeries_2019 = pd.read_csv(f'{dataDirectory}/renewable_cf2019.csv', index_col=0, parse_dates = True)


# Powerplants with capacity in MW, efficiency in percentage, emission in T_CO2/MWh,
# variableCost in EUR/MWh, technology type
powerplants = pd.read_csv(f'{dataDirectory}/2020_majorPowerplants_GER_1h.csv', index_col=0)


# Installed renewable capacity in the year 2020 for Germany given in MW
installedRenewables = {'PV': 48206,
                       'Onshore': 53184,
                       'Offshore':7504
                      }
 

#%%
plt.figure()
plt.plot(cfTimeSeries_2015["offshore"], label = "Solar_2015")
plt.plot(cfTimeSeries_2019["offshore"], label = "Solar_2019")
plt.plot(cfTimeSeries_2020["offshore"], label = "Solar_2020")
plt.legend()
plt.show()



#%% Data for all Scenarios
cfTimeSeries_2019 = cfTimeSeries_2019.resample("D").mean()
demandTimeSeries_2019 = demandTimeSeries_2019.resample("D").sum()
demandTimeSeries_2030 = demandTimeSeries_2030.resample("D").sum()
demand_max_2019 = demandTimeSeries_2019["demand"].max() # MWh
date_2019 = demandTimeSeries_2019.index[demandTimeSeries_2019['demand'] == demand_max_2019]
demand_max_2030 = demandTimeSeries_2030["Demand_2030"].max() # MWh


#total_demand_2019 = demandTimeSeries_2019["demand"].sum() / 10e5 # TWh
#total_demand_2030 = 700 # TWh according to Agora Energiewende
#demand_max_2030 = demand_max_2019 * total_demand_2030 / total_demand_2019 # MWh


"""
If we have time we should calculate everything hourly and not taking the worst demand. Because this we are assuming there is some solar during the night.
So the way would be to caclulate renewableFeedIn hourly, do the same calculations but hourly and when dividing by capacity factors assing cero in the errors.
"""



# Calculating renewable feedin (Installed capacity x Capacity factor)
solarFeedIn = installedRenewables['PV'] * cfTimeSeries_2019['solar'].loc[date_2019]
onShoreFeedIn = installedRenewables['Onshore'] * cfTimeSeries_2019['onshore'].loc[date_2019]
offShoreFeedIn = installedRenewables['Offshore'] * cfTimeSeries_2019['offshore'].loc[date_2019]
renewableFeedIn = solarFeedIn + onShoreFeedIn + offShoreFeedIn

renewableFeedIn = renewableFeedIn.values[0]

# Requiered energies to cover max demand
need_RE_S1_req = demand_max_2030 / 24 - renewableFeedIn

#%% Scenario 1: All demand is covered by Wind and PV

# Installed capacity needed to cover max demand
need_PV_S1_cap = need_RE_S1_req * (solarFeedIn / renewableFeedIn) / cfTimeSeries_2019['solar'].loc[date_2019]
need_OnShore_S1_cap = need_RE_S1_req * onShoreFeedIn / renewableFeedIn / cfTimeSeries_2019['onshore'].loc[date_2019]
need_OffShore_S1_cap = need_RE_S1_req * offShoreFeedIn / renewableFeedIn / cfTimeSeries_2019['offshore'].loc[date_2019]

need_RE_S1_cap = need_PV_S1_cap + need_OnShore_S1_cap + need_OffShore_S1_cap
need_RE_S1_cap = need_RE_S1_cap.values[0] / 10e5 # TW


#%% Scenario 2: Demand is covered by Wind and PV and gas as backup

# Define max technical potential of Wind and PV in Germany
wind onshore 2.9 TWh
# Extract natural gas power plants from powerplants database
gas_PP = powerplants[powerplants.technology == "natural gas"]
# define which gas power plants we keep and which ones we phase out


#%% Scenario 3: Demand is covered by Wind and PV and storage

# Define max technical potential of Wind and PV in Germany

# Electrolysis capacity according to coalition agreement
electrolysis_cap = 10 # GW



#------- This is for the next Scenarios: NOT FINISHED --------------
phase_out = powerplants[powerplants.technology != "nuclear"]
phase_out = phase_out[phase_out.technology != "lignite"]
phase_out = phase_out[phase_out.technology != "hard coal"]
phase_out['cumulativeSum'] = phase_out.capacity.cumsum() + renewableFeedIn
max_cap = phase_out["cumulativeSum"].max()
need_RE = demand_max - max_cap
# Remember to divide by capaccity factor and find shares of each RE
print(need_RE)


#%% Things of the original code we don't know if we are going to end up using
"""
# CHECK IF WE REALLY NEED IT

# Fuel prices in EUR/MWh with CO2 Key refers to the CO2 prices in EUR/T_CO2
fuelTimeSeries = pd.read_csv(f'{dataDirectory}/2020_fuelPrices_GER_1h.csv', index_col=0, parse_dates = True)

# Emission factors per technology type in percentage
emissionFactors = pd.read_csv(f'{dataDirectory}/2020_emissionFactors_GER_1h.csv', index_col=0)

# Dictionary defining the colors for different powerplants
#colors = {'lignite':'green', 'hard coal':'black', 'natural gas':'red', 'oil':'orange'}


colors = {'nuclear':'blue', 'lignite':'green', 'hard coal':'black', 'natural gas':'red', 'oil':'orange'}

# =============================================================================
# Importing the Validation Data (Real Market Prices for 2020)
# =============================================================================
# Real market prices in EUR/MWh given for each hour of the year 2020 for Germany
validationPricesTimeSeries = pd.read_csv(f'{dataDirectory}/2020_electricityPrices_GER_1h.csv', index_col=0, parse_dates = True)

"""
