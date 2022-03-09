# -*- coding: utf-8 -*-

import numpy as np
import pyomo.environ as pyo
from pyomo.opt import SolverFactory


def RenShareTargetOpt(data,
                      capacityFactors,
                      renewableShareTarget,
                      installedSolarCapacity,
                      installedOnWindCapacity,
                      installedOffWindCapacity,
                      other_ren_gen,
                      installedStorageCapacity,
                      storagePower,
                      initialSOC,
                      chargingEfficiency,
                      dischargingEfficiency,
                      solarCost,
                      windOnshoreCost,
                      windOffshoreCost,
                      storageCost):
    model = pyo.ConcreteModel()

    model.i = pyo.RangeSet(0, len(data)-1)

    model.solarCapacity = pyo.Var(
        domain=pyo.NonNegativeReals, bounds=(0.0, 450e3))
    model.windOnshoreCapacity = pyo.Var(domain=pyo.NonNegativeReals, bounds=(
        0.0, 930e3))  # Potential for best locations
    model.windOffshoreCapacity = pyo.Var(
        domain=pyo.NonNegativeReals, bounds=(0.0, 60e3))  # Between 50 and 70 GW

    model.storageCapacity = pyo.Var(
        domain=pyo.NonNegativeReals, bounds=(0.0, 246e3))  # in MWh 297.63e3 (with Hydro)
    model.SOC = pyo.Var(model.i, domain=pyo.NonNegativeReals)
    model.charge = pyo.Var(model.i, domain=pyo.NonNegativeReals)
    model.discharge = pyo.Var(model.i, domain=pyo.NonNegativeReals)

    model.renGen = pyo.Var(model.i, domain=pyo.NonNegativeReals)
    model.conventionalGen = pyo.Var(model.i, domain=pyo.NonNegativeReals)

    model.renShare = pyo.Var(model.i, domain=pyo.NonNegativeReals)

    model.investmentCost = pyo.Var(domain=pyo.NonNegativeReals)
    model.curtailment = pyo.Var(model.i, domain=pyo.NonNegativeReals)

    def energyBalance_rule(model, i):
        return data['demand'].iat[i] + model.curtailment[i] + model.charge[i] == model.renGen[i] + model.discharge[i] + model.conventionalGen[i]

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
        return (renewableShareTarget-0.01, pyo.summation(model.renShare)/len(data), renewableShareTarget+0.01)

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


def run(data,
        capacityFactors,
        renewableShareTarget,
        installedSolarCapacity,
        installedOnWindCapacity,
        installedOffWindCapacity,
        other_ren_gen,
        installedStorageCapacity,
        storagePower,
        initialSOC,
        chargingEfficiency,
        dischargingEfficiency,
        solarCost,
        windOnshoreCost,
        windOffshoreCost,
        storageCost):

    model = RenShareTargetOpt(data=data,
                              capacityFactors=capacityFactors,
                              renewableShareTarget=renewableShareTarget,
                              installedSolarCapacity=installedSolarCapacity,
                              installedOnWindCapacity=installedOnWindCapacity,
                              installedOffWindCapacity=installedOffWindCapacity,
                              other_ren_gen=other_ren_gen,
                              installedStorageCapacity=installedStorageCapacity,
                              storagePower=storagePower,
                              initialSOC=initialSOC,
                              chargingEfficiency=chargingEfficiency,
                              dischargingEfficiency=dischargingEfficiency,
                              solarCost=solarCost,
                              windOnshoreCost=windOnshoreCost,
                              windOffshoreCost=windOffshoreCost,
                              storageCost=storageCost)

    renShare, convGen, curtailed, renGen = get_values(model,data)
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
    print("Extra storage capacity GWh:", round(
        model.storageCapacity.value/1000, 2))
