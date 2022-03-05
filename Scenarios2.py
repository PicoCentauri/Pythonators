# -*- coding: utf-8 -*-
"""
Created on Sat Mar  5 16:34:07 2022

@author: moham
"""

import numpy as np
import pandas as pd #import pandas to work with dataframes

import pyomo.environ as pyo
from pyomo.opt import SolverFactory

import matplotlib.pyplot as plt

# %%
capacityFactors = pd.read_csv('data/renewable_cf2019.csv', index_col=0, parse_dates = True)
other_ren_gen = pd.read_csv('data/2020_other_ren_gen_1h.csv', index_col=0, parse_dates = True)
# Demand data for 2030
data = pd.read_csv('data/demand_2030.csv', index_col=0, parse_dates = True) # in MWh

# Capacities for 2021
installedSolarCapacity = 58980 #MW
installedOnWindCapacity = 56270 #MW
installedOffWindCapacity = 7770 #MW

#%% Costs for 2030 (Source: paper table 4)
solarCost = 254e-3 #mln EUR per MW installed capacity
windOnshoreCost = 1035e-3 #mln EUR per MW installed capacity
windOffshoreCost = 1934e-3 #mln EUR per MW installed capacity
storageCost = 142e-3 #mln EUR per MWh installed capacity

chargingEfficiency = 0.82
dischargingEfficiency = 0.92
initialSOC = 0.5 #initial State of Charge (ratio from capacity)

# %%
def RenShareTargetOpt(data, capacityFactors, renewableShareTarget, installedStorageCapacity, storagePower):
    model = pyo.ConcreteModel()
    
    model.i = pyo.RangeSet(0, len(data)-1)
        
    model.solarCapacity = pyo.Var(domain=pyo.NonNegativeReals, bounds = (0.0, 450e3)) 
    model.windOnshoreCapacity = pyo.Var(domain=pyo.NonNegativeReals, bounds = (0.0, 930e3)) # Potential for best locations
    model.windOffshoreCapacity = pyo.Var(domain=pyo.NonNegativeReals, bounds = (0.0, 60e3)) # Between 50 and 70 GW
    
    model.storageCapacity = pyo.Var(domain=pyo.NonNegativeReals)
    model.SOC = pyo.Var(model.i, domain=pyo.NonNegativeReals)
    model.charge = pyo.Var(model.i, domain=pyo.NonNegativeReals)
    model.discharge = pyo.Var(model.i, domain=pyo.NonNegativeReals)
    
    
    model.renGen = pyo.Var(model.i, domain=pyo.NonNegativeReals)
    model.conventionalGen = pyo.Var(model.i, domain=pyo.NonNegativeReals)
    
    model.renShare = pyo.Var(model.i, domain=pyo.NonNegativeReals)
    
    model.investmentCost = pyo.Var(domain=pyo.NonNegativeReals)
    model.curtailment = pyo.Var(model.i, domain=pyo.NonNegativeReals)
    
    def energyBalance_rule(model, i):
        return data['demand'].iat[i] + model.curtailment[i] + model.charge[i] ==  model.renGen[i] + model.discharge[i] + model.conventionalGen[i]


    def renGen_rule(model, i):
        return model.renGen[i] == (model.solarCapacity + installedSolarCapacity) * capacityFactors['solar'].iat[i] \
            + (model.windOnshoreCapacity + installedOnWindCapacity) * capacityFactors['onshore'].iat[i] \
            + (model.windOffshoreCapacity + installedOffWindCapacity) * capacityFactors['offshore'].iat[i] \
            + other_ren_gen.iloc[i].sum()
            
            
    def SOC_rule(model, i):
        if i == 0:
            return model.SOC[i] == initialSOC * (installedStorageCapacity + model.storageCapacity) + model.charge[i] * chargingEfficiency - model.discharge[i] / dischargingEfficiency
        else:
            return model.SOC[i] == model.SOC[i-1] + model.charge[i] * chargingEfficiency - model.discharge[i] / dischargingEfficiency
    
    
    def batteryCapacity_rule(model, i):
        return model.SOC[i] <= model.storageCapacity + installedStorageCapacity
    
    def batteryPower_rule(model, i):
        return model.charge[i] + model.discharge[i] <= storagePower + 0.3*model.storageCapacity
    
    def renShare_rule(model, i):
        return model.renShare[i] == 1 - model.conventionalGen[i] / data['demand'].iat[i]
    
    def renShareTarget_rule(model):
        return (renewableShareTarget, pyo.summation(model.renShare)/len(data), renewableShareTarget)
    
    def investmentCost_rule(model):
        return model.investmentCost == solarCost*model.solarCapacity + windOnshoreCost*model.windOnshoreCapacity\
            + windOffshoreCost*model.windOffshoreCapacity + storageCost*model.storageCapacity
    
    def curtailment_rule(model):
        return pyo.summation(model.curtailment) <= 0.2*pyo.summation(model.renGen)
    
    model.renGen_rule = pyo.Constraint(model.i, rule=renGen_rule)
    model.SOC_rule = pyo.Constraint(model.i, rule=SOC_rule)
    model.energyBalance_rule = pyo.Constraint(model.i, rule=energyBalance_rule)
    model.renShare_rule = pyo.Constraint(model.i, rule=renShare_rule)
    model.investmentCost_rule = pyo.Constraint(rule=investmentCost_rule)
    model.renShareTarget_rule = pyo.Constraint(rule=renShareTarget_rule)
    model.batteryCapacity_rule = pyo.Constraint(model.i, rule = batteryCapacity_rule)
    model.batteryPower_rule = pyo.Constraint(model.i, rule = batteryPower_rule)

    #model.curtailment_rule = pyo.Constraint(rule=curtailment_rule)
    
    def ObjRule(model):
        return model.investmentCost
     
    model.obj = pyo.Objective(rule = ObjRule, sense = pyo.minimize)
    
    opt = SolverFactory("glpk")
    
    opt.solve(model)
    
    return model

def get_values(model):
    renShare = []
    convGen = []
    curtailed = []  
    renGen = []
    
    for i in range(len(data)):
        renShare.append(model.renShare[i].value)
        convGen.append(model.conventionalGen[i].value)
        curtailed.append(model.curtailment[i].value)
        renGen.append(model.renGen[i].value)

    return renShare, convGen, curtailed, renGen 

# %%
installedStorageCapacity = 580e3 # in MW
storagePower = 10.8e3 #in MW # Look for that later
renewableShareTarget = 1

model = RenShareTargetOpt(data = data,
                          capacityFactors = capacityFactors,
                          renewableShareTarget = renewableShareTarget,
                          installedStorageCapacity = installedStorageCapacity,
                          storagePower = storagePower)

renShare, convGen, curtailed, renGen = get_values(model) 
curtailedPercentage = sum(curtailed) / sum(renGen) * 100

investment = round(model.investmentCost.value/1000, 3)

print("Renewable share:", (np.average(renShare)))
print("Investment cost:", investment, "billion €")
print("Curtailment (%):", curtailedPercentage)

print("Extra solar capacity GW:", round(model.solarCapacity.value/1000, 2))
print("Extra wind onshore capacity GW:", round(model.windOnshoreCapacity.value/1000, 2))
print("Extra wind offshore capacity GW:", round(model.windOffshoreCapacity.value/1000, 2))
print("Extra storage capacity GWh:", round(model.storageCapacity.value/1000, 2))

# %% Scenario 2 with Gas

def RenShareTargetOpt(data, capacityFactors, installedStorageCapacity, storagePower):
    model = pyo.ConcreteModel() #renewableShareTarget
    
    model.i = pyo.RangeSet(0, len(data)-1)
        
    model.solarCapacity = pyo.Var(domain=pyo.NonNegativeReals, bounds = (0.0, 450e3)) 
    model.windOnshoreCapacity = pyo.Var(domain=pyo.NonNegativeReals, bounds = (0.0, 930e3)) # Potential for best locations
    model.windOffshoreCapacity = pyo.Var(domain=pyo.NonNegativeReals, bounds = (0.0, 60e3)) # Between 50 and 70 GW
    
    model.storageCapacity = pyo.Var(domain=pyo.NonNegativeReals)
    model.SOC = pyo.Var(model.i, domain=pyo.NonNegativeReals)
    model.charge = pyo.Var(model.i, domain=pyo.NonNegativeReals)
    model.discharge = pyo.Var(model.i, domain=pyo.NonNegativeReals)
    
    
    model.renGen = pyo.Var(model.i, domain=pyo.NonNegativeReals)
    model.conventionalGen = pyo.Var(model.i, domain=pyo.NonNegativeReals, bounds = (0.0, 31.68e3)) # For Gas
    
    model.renShare = pyo.Var(model.i, domain=pyo.NonNegativeReals)
    
    model.investmentCost = pyo.Var(domain=pyo.NonNegativeReals)
    model.curtailment = pyo.Var(model.i, domain=pyo.NonNegativeReals)
    
    def energyBalance_rule(model, i):
        return data['demand'].iat[i] + model.curtailment[i] + model.charge[i] ==  model.renGen[i] + model.discharge[i] + model.conventionalGen[i]


    def renGen_rule(model, i):
        return model.renGen[i] == (model.solarCapacity + installedSolarCapacity) * capacityFactors['solar'].iat[i] \
            + (model.windOnshoreCapacity + installedOnWindCapacity) * capacityFactors['onshore'].iat[i] \
            + (model.windOffshoreCapacity + installedOffWindCapacity) * capacityFactors['offshore'].iat[i] \
            + other_ren_gen.iloc[i].sum()
            
            
    def SOC_rule(model, i):
        if i == 0:
            return model.SOC[i] == initialSOC * (installedStorageCapacity + model.storageCapacity) + model.charge[i] * chargingEfficiency - model.discharge[i] / dischargingEfficiency
        else:
            return model.SOC[i] == model.SOC[i-1] + model.charge[i] * chargingEfficiency - model.discharge[i] / dischargingEfficiency
    
    
    def batteryCapacity_rule(model, i):
        return model.SOC[i] <= model.storageCapacity + installedStorageCapacity
    
    def batteryPower_rule(model, i):
        return model.charge[i] + model.discharge[i] <= storagePower + 0.3*model.storageCapacity
    
    def renShare_rule(model, i):
        return model.renShare[i] == 1 - model.conventionalGen[i] / data['demand'].iat[i]
    
   # def renShareTarget_rule(model):
      #  return (renewableShareTarget, pyo.summation(model.renShare)/len(data), renewableShareTarget)
    
    def investmentCost_rule(model):
        return model.investmentCost == solarCost*model.solarCapacity + windOnshoreCost*model.windOnshoreCapacity\
            + windOffshoreCost*model.windOffshoreCapacity + storageCost*model.storageCapacity
    
    def curtailment_rule(model):
        return pyo.summation(model.curtailment) <= 0.2*pyo.summation(model.renGen)
    
    model.renGen_rule = pyo.Constraint(model.i, rule=renGen_rule)
    model.SOC_rule = pyo.Constraint(model.i, rule=SOC_rule)
    model.energyBalance_rule = pyo.Constraint(model.i, rule=energyBalance_rule)
    model.renShare_rule = pyo.Constraint(model.i, rule=renShare_rule)
    model.investmentCost_rule = pyo.Constraint(rule=investmentCost_rule)
    #model.renShareTarget_rule = pyo.Constraint(rule=renShareTarget_rule)
    model.batteryCapacity_rule = pyo.Constraint(model.i, rule = batteryCapacity_rule)
    model.batteryPower_rule = pyo.Constraint(model.i, rule = batteryPower_rule)

    #model.curtailment_rule = pyo.Constraint(rule=curtailment_rule)
    
    def ObjRule(model):
        return model.investmentCost
     
    model.obj = pyo.Objective(rule = ObjRule, sense = pyo.minimize)
    
    opt = SolverFactory("glpk")
    
    opt.solve(model)
    
    return model

def get_values(model):
    renShare = []
    convGen = []
    curtailed = []  
    renGen = []
    
    for i in range(len(data)):
        renShare.append(model.renShare[i].value)
        convGen.append(model.conventionalGen[i].value)
        curtailed.append(model.curtailment[i].value)
        renGen.append(model.renGen[i].value)

    return renShare, convGen, curtailed, renGen 

# %%
installedStorageCapacity = 580e3 # in MW
storagePower = 10.8e3 #in MW # Look for that later
#renewableShareTarget = 0.8

model = RenShareTargetOpt(data = data,
                          capacityFactors = capacityFactors,
                          #renewableShareTarget = renewableShareTarget,
                          installedStorageCapacity = installedStorageCapacity,
                          storagePower = storagePower)

renShare, convGen, curtailed, renGen = get_values(model) 
curtailedPercentage = sum(curtailed) / sum(renGen) * 100

investment = round(model.investmentCost.value/1000, 3)

print("Renewable share:", (np.average(renShare)))
print("Investment cost:", investment, "billion €")
print("Curtailment (%):", curtailedPercentage)

print("Extra solar capacity GW:", round(model.solarCapacity.value/1000, 2))
print("Extra wind onshore capacity GW:", round(model.windOnshoreCapacity.value/1000, 2))
print("Extra wind offshore capacity GW:", round(model.windOffshoreCapacity.value/1000, 2))
print("Extra storage capacity GWh:", round(model.storageCapacity.value/1000, 2))
#print("Gas capacity GW:", round(model.conventionalGen.value/1000, 2))