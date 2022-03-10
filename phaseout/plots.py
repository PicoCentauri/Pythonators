#!/usr/bin/env python3
# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
"""

Plot results.

Student 1 name: Mohamed Eltoukhy, 5170372
Student 2 name: Anna Lebowsky, 5143788

"""
import numpy as np
import mpltex  # for nice plots
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms

from mpltex.acs import _height, width_double_column
from matplotlib import dates  # for e.g. months as labels


@mpltex.acs_decorator
def plot_demand(data):
    fig, ax = plt.subplots()

    ax.plot(data.index, data.demand)

    # Only show month
    hfmt = dates.DateFormatter('%m')
    ax.xaxis.set_major_formatter(hfmt)
    ax.set_xlabel("Month")

    ax.set_ylabel('Demand in MWh')

    fig.tight_layout()
    fig.savefig("output/demand2030.pdf", transparent=True, bbox_inches="tight")
    fig.show()


@mpltex.acs_decorator
def plot_investments(labels, investments):
    fig, ax = plt.subplots()

    ax.barh(labels, investments)

    ax.set_xlabel('Investment cost in billion €')

    fig.tight_layout()
    fig.savefig("output/investments.pdf",
                transparent=True,
                bbox_inches="tight")
    fig.show()