#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 11 20:55:57 2022
 
"""

# imports for MCDA
import matplotlib.pyplot as plt
from skcriteria import mkdm
from skcriteria.madm import similarity  # here lives TOPSIS
from skcriteria.pipeline import mkpipe
from skcriteria.preprocessing import invert_objectives, scalers

# =============================================================================
# At the very beginning we need to read all the files: demand, capacity
# =============================================================================




# =============================================================================
# Read cvs files
# =============================================================================

# =============================================================================
# MCDA Analysis
# =============================================================================


# 4 alternatives by 4 criteria
mtx = [[100, 80, 100, 150, 10, 1e-6], 
       [80, 70, 75, 75, 10, 25], 
       [20, 40, 5, 200, 40, 75], 
       [1e-6, 100, 1e-6, 10, 100, 100], 
       [40, 10, 90, 250, 30, 50], 
       [70, 30, 40, 100, 10, 50],
       [80, 1e-6, 50, 350, 10, 75],
       [50, 20, 90, 550, 40, 50],
       [20, 20, 30, 50, 50, 25]] #Emotions

weights = [0.1, 0.2, 0.2, 0.3, 0.05, 0.15]

# The first three alternatives are for maximization and the last one for minimization
alternative_name = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
criteria_name = ["Economic", "Sustaibility", "Usability", "Cost", "Packaging", "Emotions"]
criteria_type = [max, max, max, min, min, max]

dm = mkdm(matrix = mtx,
          objectives = criteria_type,
          weights = weights,
          alternatives = alternative_name,
          criteria = criteria_name)

inverter = invert_objectives.MinimizeToMaximize()
dmt = inverter.transform(dm)

scaler = scalers.SumScaler(target="both")
dmt = scaler.transform(dmt)

pipe = mkpipe(invert_objectives.MinimizeToMaximize(),
              scalers.VectorScaler(target="matrix"),  # this scaler transform the matrix
              scalers.SumScaler(target="weights"),  # and this transform the weights
              similarity.TOPSIS(),
)

decision = pipe.evaluate(dm)

print(decision)
print(decision.e_)
print("Ideal:", decision.e_.ideal)
print("Anti-Ideal:", decision.e_.anti_ideal)
print("Closeness:", decision.e_.similarity)


plt.figure()
plt.bar(alternative_name, decision.e_.similarity)
plt.ylabel('Relative Closeness')
plt.xlabel("Alternatives")
plt.show()
