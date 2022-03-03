# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 09:42:20 2021

@author: Gonzalo
"""

import matplotlib.pyplot as plt

from skcriteria import mkdm
from skcriteria.madm import similarity #Here lives TOPSIS
from skcriteria.pipeline import mkpipe
from skcriteria.preprocessing import invert_objectives, scalers

# 4 altervatives by 4 criteria
mtx = [[100, 80 , 100, 150, 10 , 0],
       [80 , 70 , 75 , 75 , 10 , 25],
       [20 , 40 , 5  , 200, 40 , 75],
       [0  , 100, 0  , 10 , 100, 100],
       [40 , 10 , 90 , 250, 30 , 50],
       [70 , 30 , 40 , 100, 10 , 50],
       [80 , 0  , 50 , 350, 10 , 75],
       [50 , 20 , 90 , 550, 40 , 50],
       [20 , 20 , 30 , 50 , 50 , 25]] 
# Our alternative will be the 3 scenarios: wind and PV only; wind, PV and gas power plants as backup, and wind, PV and electrolysis


weights = [0.1, 0.15, 0.3, 0.25, 0.2]

criteria_names = ["infrastructure", "electricity_price", "energy_security", "CO2_emissions", "availability"]

criteria_type = [min, min, max, min, max]

alternatives_names = ["Scenario 1", "Scenario 2", "Scenario 3"]

# Desicion matrix (dm)
dm = mkdm(matrix = mtx,
          objectives = criteria_type,
          weights = weights,
          criteria = criteria_names,
          alternatives = alternatives_names)

'''
inverter = invert_objectives.MinimizeToMaximize()
dmt = inverter.transform(dm)

scaler = scalers.VectorScaler(target = "matrix")
dmt = scaler.transform(dmt)
'''

pipe = mkpipe(invert_objectives.MinimizeToMaximize(),
              scalers.VectorScaler(target="matrix"),# this scaler transform the matrix
              scalers.SumScaler(target="weights"),#and this transforms the weights
              similarity.TOPSIS())

decision = pipe.evaluate(dm)

print(decision)
print()
print(decision.e_)
print()

print()