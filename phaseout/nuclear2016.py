# -*- coding: utf-8 -*-
"""
Created on Wed Mar  9 21:52:32 2022

@author: moham
"""

import numpy as np
import pyomo.environ as pyo
from pyomo.opt import SolverFactory


def RenShareTargetOpt(data,
                      capacityFactors,
                      renewableShareTarget,
                      installedSolarCapacity,
                      installedOnWindCapacity,
                      installedOffWindCapacity,
                      installedGasCapacity,
                      other_ren_gen,
                      installedStorageCapacity,
                      storagePower,
                      initialSOC,
                      chargingEfficiency,
                      dischargingEfficiency,
                      solarCost,
                      windOnshoreCost,
                      windOffshoreCost,
                      storageCost,
                      gasCost):
    model = pyo.ConcreteModel()

    model.i = pyo.RangeSet(0, len(data)-1)

    model.solarCapacity = pyo.Var(
        domain=pyo.NonNegativeReals, bounds=(0.0, 450e3))
    model.windOnshoreCapacity = pyo.Var(domain=pyo.NonNegativeReals, bounds=(
        0.0, 930e3))  # Potential for good locations 2.200 full load hours
    model.windOffshoreCapacity = pyo.Var(
        domain=pyo.NonNegativeReals, bounds=(0.0, 60e3))  # Between 50 and 70 GW
    model.gasCapacity = pyo.Var(domain=pyo.NonNegativeReals)

    model.storageCapacity = pyo.Var(
        domain=pyo.NonNegativeReals, bounds=(0.0, 246e3))  # in MWh
    model.SOC = pyo.Var(model.i, domain=pyo.NonNegativeReals)
    model.charge = pyo.Var(model.i, domain=pyo.NonNegativeReals)
    model.discharge = pyo.Var(model.i, domain=pyo.NonNegativeReals)

    model.renGen = pyo.Var(model.i, domain=pyo.NonNegativeReals)
    model.nuclearGen = pyo.Var(model.i, domain=pyo.NonNegativeReals, bounds=(0.0, 10.8e3)) # in MWh
    model.gasGen = pyo.Var(model.i, domain=pyo.NonNegativeReals)

    model.renShare = pyo.Var(model.i, domain=pyo.NonNegativeReals)

    model.investmentCost = pyo.Var(domain=pyo.NonNegativeReals)
    model.curtailment = pyo.Var(model.i, domain=pyo.NonNegativeReals)

    def energyBalance_rule(model, i):
        return data['demand'].iat[i] + model.curtailment[i] + model.charge[i] == model.renGen[i] + model.discharge[i] + model.nuclearGen[i] + model.gasGen[i]

    def renGen_rule(model, i):
        return model.renGen[i] == (model.solarCapacity + installedSolarCapacity) * capacityFactors['solar'].iat[i] \
            + (model.windOnshoreCapacity + installedOnWindCapacity) * capacityFactors['onshore'].iat[i] \
            + (model.windOffshoreCapacity + installedOffWindCapacity) * capacityFactors['offshore'].iat[i] \
            + other_ren_gen.iloc[i].sum()
    
    def gasGen_rule(model, i):
        return model.gasGen[i] <= (model.gasCapacity + installedGasCapacity)

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
        return model.renShare[i] == 1 - model.nuclearGen[i] / data['demand'].iat[i]

    def renShareTarget_rule(model):
        return (renewableShareTarget, pyo.summation(model.renShare)/len(data), renewableShareTarget)

    def investmentCost_rule(model):
        return model.investmentCost == solarCost*model.solarCapacity + windOnshoreCost*model.windOnshoreCapacity\
            + windOffshoreCost*model.windOffshoreCapacity + storageCost*model.storageCapacity + gasCost*model.gasCapacity

    def curtailment_rule(model):
        return pyo.summation(model.curtailment) <= 0.2*pyo.summation(model.renGen)

    model.renGen_rule = pyo.Constraint(model.i, rule=renGen_rule)
    model.gasGen_rule = pyo.Constraint(model.i, rule=gasGen_rule)
    model.SOC_rule = pyo.Constraint(model.i, rule=SOC_rule)
    model.energyBalance_rule = pyo.Constraint(model.i, rule=energyBalance_rule)
    model.renShare_rule = pyo.Constraint(model.i, rule=renShare_rule)
    model.investmentCost_rule = pyo.Constraint(rule=investmentCost_rule)
    model.renShareTarget_rule = pyo.Constraint(rule=renShareTarget_rule)
    model.batteryCapacity_rule = pyo.Constraint(
        model.i, rule=batteryCapacity_rule)
    model.batteryPower_rule = pyo.Constraint(model.i, rule=batteryPower_rule)

    model.curtailment_rule = pyo.Constraint(rule=curtailment_rule)

    def ObjRule(model):
        return model.investmentCost

    model.obj = pyo.Objective(rule=ObjRule, sense=pyo.minimize)

    opt = SolverFactory("glpk")

    opt.solve(model)

    return model


def get_values(model, data):
    renShare = []
    curtailed = []
    renGen = []
    nuclearGen = []
    gasGen = []

    for i in range(len(data)):
        renShare.append(model.renShare[i].value)
        curtailed.append(model.curtailment[i].value)
        renGen.append(model.renGen[i].value)
        nuclearGen.append(model.nuclearGen[i].value)
        gasGen.append(model.gasGen[i].value)

    return renShare, curtailed, renGen, nuclearGen, gasGen

# %%
def run(data,
        capacityFactors,
        renewableShareTarget,
        installedSolarCapacity,
        installedOnWindCapacity,
        installedOffWindCapacity,
        installedGasCapacity,
        other_ren_gen,
        installedStorageCapacity,
        storagePower,
        initialSOC,
        chargingEfficiency,
        dischargingEfficiency,
        solarCost,
        windOnshoreCost,
        windOffshoreCost,
        storageCost,
        gasCost):

    model = RenShareTargetOpt(data=data,
                              capacityFactors=capacityFactors,
                              renewableShareTarget=renewableShareTarget,
                              installedSolarCapacity=installedSolarCapacity,
                              installedOnWindCapacity=installedOnWindCapacity,
                              installedOffWindCapacity=installedOffWindCapacity,
                              installedGasCapacity=installedGasCapacity,
                              other_ren_gen=other_ren_gen,
                              installedStorageCapacity=installedStorageCapacity,
                              storagePower=storagePower,
                              initialSOC=initialSOC,
                              chargingEfficiency=chargingEfficiency,
                              dischargingEfficiency=dischargingEfficiency,
                              solarCost=solarCost,
                              windOnshoreCost=windOnshoreCost,
                              windOffshoreCost=windOffshoreCost,
                              storageCost=storageCost,
                              gasCost=gasCost)

    renShare, curtailed, renGen, nuclearGen, gasGen = get_values(model,data)
    curtailedPercentage = sum(curtailed) / sum(renGen) * 100

    investment = round(model.investmentCost.value/1000, 3)

    print("Renewable share:", (np.average(renShare)))
    print("Investment cost:", investment, "billion €")
    print("Curtailment (%):", curtailedPercentage)

    print("Extra solar capacity GW:", round(model.solarCapacity.value/1000, 2))
    print("Extra wind onshore capacity GW:", round(
        model.windOnshoreCapacity.value/1000, 2))
    print("Extra wind offshore capacity GW:", round(
        model.windOffshoreCapacity.value/1000, 2))
    print("Extra gas capacity GW:", round(
        model.gasCapacity.value/1000, 2))
    print("Extra storage capacity GWh:", round(
        model.storageCapacity.value/1000, 2))
