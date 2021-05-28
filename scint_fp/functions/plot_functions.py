# Beth Saunders 27/05/21
# functions creating plots go here

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec


def plot_L(L, time):
    """
    Function to prodice a plot for L
    """

    # seperate positive and negative vals
    L_positive = np.ma.masked_where(L < 0, L, copy=True)
    L_positive_times = np.ma.masked_where(L > 0, time, copy=True)
    L_negative = np.ma.masked_where(L > 0, L, copy=True)
    L_negative_times = np.ma.masked_where(L < 0, time, copy=True)

    # plotting
    fig = plt.figure()
    # set height ratios for subplots
    gs = gridspec.GridSpec(2, 1, height_ratios=[1, 1])

    # the first subplot
    ax1 = plt.subplot(gs[0])
    # log scale for axis Y of the first subplot
    ax1.set_yscale("log")
    line1, = ax1.plot(L_positive_times, L_positive, color='red', marker='o', linestyle=None)

    # the second subplot
    # shared axis X
    ax2 = plt.subplot(gs[1], sharex=ax1)
    ax2.set_yscale('log')
    line2, = ax2.plot(L_negative_times, L_negative*-1, color='blue', marker='o', linestyle=None)
    ax2.set_ylim(ax2.get_ylim()[::-1])

    plt.setp(ax1.get_xticklabels(), visible=False)
    # remove last tick label for the second subplot
    yticks = ax2.yaxis.get_major_ticks()
    yticks[-1].label1.set_visible(False)

    # put legend on first subplot
    ax2.legend((line1, line2), ('Positive L', 'Negative L'), loc='upper left')

    # remove vertical gap between subplots
    plt.subplots_adjust(hspace=.0)

    plt.gcf().autofmt_xdate()

    plt.show()


def generic_plot_vs_time(var, time, varname):
    """
    Function to plot any var vs time
    """

    plt.figure()
    plt.scatter(var, time)
    plt.ylabel(varname)
    plt.xlabel('time')
    plt.gcf().autofmt_xdate()
    plt.show()
