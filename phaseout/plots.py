#!/usr/bin/env python3
# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
"""
Plot functions.

"""
import numpy as np
import mpltex  # for nice plots
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms

from mpltex.acs import _height, width_double_column
from matplotlib import dates # for e.g. months as labels

@mpltex.acs_decorator
def plot_demand(data):
    fig, ax = plt.subplots()

    ax.plot(data.index, data.demand)

    # Only show month
    hfmt = dates.DateFormatter('%m')
    ax.xaxis.set_major_formatter(hfmt)
    ax.set_xlabel("Month")

    ax.set_ylabel('Hourly demand in MWh')
    ax.legend()
    ax.minorticks_on()

    fig.tight_layout()
    fig.savefig("output/demand2030.pdf", transparent=True, bbox_inches="tight")
    fig.show()

#plot_demand()

@mpltex.acs_decorator
def plot_investments(data, bars, investments):
    fig, ax = plt.subplots()

    ax.plot(data.index, data.demand)

    y_pos = np.arange(len(bars))
 
    # Create horizontal bars
    # Create horizontal bars
    ax.barh(y=investments.index, width=investments.value);
 
    # Only show month
    hfmt = dates.DateFormatter('%m')
    ax.xaxis.set_major_formatter(hfmt)
    ax.set_xlabel("Month")

    ax.set_ylabel('Hourly demand in MWh')
    ax.legend()
    ax.minorticks_on()

    fig.tight_layout()
    fig.savefig("output/investments.pdf", transparent=True, bbox_inches="tight")
    fig.show()