# Beth Saunders 27/05/21
# functions creating plots go here

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.dates import DateFormatter


def plot_L(L, time, stability_class):
    """
    Function to prodice a plot for L
    """

    index_stable = np.where(np.asarray(stability_class) == 1)[0]
    index_unstable = np.where(np.asarray(stability_class) == -1)[0]
    index_neutral = np.where(np.asarray(stability_class) == 0)[0]

    stable_hours = time[index_stable]
    unstable_hours = time[index_unstable]
    neutral_hours = time[index_neutral]

    where_stable = np.isin(time, stable_hours)
    where_unstable = np.isin(time, unstable_hours)
    where_neutral = np.isin(time, neutral_hours)

    unstable_L = np.ma.masked_array(L, mask=[not i for i in where_unstable])
    stable_L = np.ma.masked_array(L, mask=[not i for i in where_stable])
    neutral_L = np.ma.masked_array(L, mask=[not i for i in where_neutral])

    # seperate positive and negative vals in neutral L
    neutral_L_positive = np.ma.masked_where(neutral_L < 0, L, copy=True)
    neutral_L_negative = np.ma.masked_where(neutral_L > 0, L, copy=True)

    # plotting
    fig = plt.figure()
    # set height ratios for subplots
    gs = gridspec.GridSpec(2, 1, height_ratios=[1, 1])

    # the first subplot
    # Positive values of L - stable and some neutral cases
    ax1 = plt.subplot(gs[0])
    # log scale for axis Y of the first subplot
    ax1.set_yscale("log")
    line1, = ax1.plot(time, stable_L, color='red', marker='o', linestyle=None)
    line2, = ax1.plot(time, neutral_L_positive, color='green', marker='o', linestyle=None)

    # the second subplot
    # shared axis X
    ax2 = plt.subplot(gs[1], sharex=ax1)
    ax2.set_yscale('log')
    line3, = ax2.plot(time, unstable_L * -1, color='blue', marker='o', linestyle=None)
    line4, = ax2.plot(time, neutral_L_negative * -1, color='green', marker='o', linestyle=None)
    ax2.set_ylim(ax2.get_ylim()[::-1])

    plt.setp(ax1.get_xticklabels(), visible=False)
    # remove last tick label for the second subplot
    yticks = ax2.yaxis.get_major_ticks()
    yticks[-1].label1.set_visible(False)

    # put legend on first subplot
    ax2.legend((line1, line2, line3), ('Stable', 'Neutral', 'Unstable'), loc='upper left')

    # remove vertical gap between subplots
    plt.subplots_adjust(hspace=.0)

    plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_formatter(DateFormatter("%H"))

    plt.xlabel('Time (h)')
    plt.ylabel('L (m)')

    plt.show()


def generic_plot_vs_time(var, time, varname, stability_class):
    """
    Function to plot any var vs time
    """

    index_stable = np.where(np.asarray(stability_class) == 1)[0]
    index_unstable = np.where(np.asarray(stability_class) == -1)[0]
    index_neutral = np.where(np.asarray(stability_class) == 0)[0]

    stable_hours = time[index_stable]
    unstable_hours = time[index_unstable]
    neutral_hours = time[index_neutral]

    where_stable = np.isin(time, stable_hours)
    where_unstable = np.isin(time, unstable_hours)
    where_neutral = np.isin(time, neutral_hours)

    unstable_var = np.ma.masked_array(var, mask=[not i for i in where_unstable])
    stable_var = np.ma.masked_array(var, mask=[not i for i in where_stable])
    neutral_var = np.ma.masked_array(var, mask=[not i for i in where_neutral])

    plt.figure()
    plt.plot(time, stable_var, marker='o', color='red')
    plt.plot(time, unstable_var, marker='o', color='blue')
    plt.plot(time, neutral_var, marker='o', color='green')
    plt.ylabel(varname)
    plt.xlabel('Time (h)')
    plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_formatter(DateFormatter("%H"))
    plt.show()


def plot_wind_components(time, ws, wd, wind_components):
    """
    Plot u and v components of wind
    Returns
    -------

    """

    u_vals = wind_components['u']
    v_vals = wind_components['v']

    fig, ax = plt.subplots()

    ax.plot(time.tolist(), u_vals, alpha=0.2, color='blue')
    ax.scatter(time.tolist(), u_vals, label='u', marker='^', color='blue')

    ax.plot(time.tolist(), v_vals, alpha=0.2, color='orange')
    ax.scatter(time.tolist(), v_vals, label='v', marker='v', color='orange')

    ax.plot(time.tolist(), ws, label='ws', linestyle='None', marker='x', color='red')

    ax2 = ax.twinx()
    ax2.plot(time.tolist(), wd, label='dir', linestyle='None', marker='.', color='green')

    plt.gcf().autofmt_xdate()
    ax.xaxis.set_major_formatter(DateFormatter('%j %H:%M'))

    ax.set_ylabel('m s$^{-1}$')
    ax2.set_ylabel('Wind Direction ($^{\circ}$)')
    ax2.set_xlabel('DOY')

    # ask matplotlib for the plotted objects and their labels
    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc=0)

    plt.show()


def stability_iteration_plots(stability_vars, savepath):
    """
    Makes plots of values for each iteration
    """

    iteration_count = stability_vars['iteration_count']
    iterations_L = stability_vars['iterations_L']
    iterations_ustar = stability_vars['iterations_ustar']

    for hour_string in sorted(iterations_L.keys()):

        print(hour_string)

        hour = int(hour_string)
        hour_index = hour - 1
        # index is -1 from the hour, as hour 0 (midnight) is for the day after the start
        # so starts at 1am, and ends midnight next day
        # 1am is item [0] in lists, midnight is last item [-1]

        L_iterations = iterations_L[hour_string]
        ustar_iterations = iterations_ustar[hour_string]
        num_of_iters = iteration_count[hour_index]

        if np.isnan(L_iterations[-1]):
            pass
        else:

            # check to see if iterations logged is the same length of iteration count (+1 for initial val)
            assert len(L_iterations) - 1 == num_of_iters

            # check to see if iterations of L all have the same sign
            assert all(item >= 0 for item in L_iterations) or all(item < 0 for item in L_iterations)

            plt.figure()
            plt.title('hour ' + hour_string)
            iteration = list(range(len(ustar_iterations)))
            plt.scatter(iteration, ustar_iterations)
            plt.xlabel('Iteration number')
            plt.ylabel('u*')
            plt.savefig(savepath + 'ustar' + '_' + hour_string + '.png')

            plt.figure()
            plt.title('hour ' + hour_string)
            iteration = list(range(len(L_iterations)))

            if L_iterations[0] < 0:
                plt.scatter(iteration, -1 * np.asarray(L_iterations))
                plt.gca().set_ylim(plt.gca().get_ylim()[::-1])
            else:
                plt.scatter(iteration, L_iterations)
            plt.xlabel('Iteration number')
            plt.ylabel('L')
            plt.yscale("log")
            plt.savefig(savepath + 'L' + '_' + hour_string + '.png')


def classify_stability(times,
                       zeff,
                       L):
    """

    :param times:
    :param zeff:
    :param L:
    :return:
    """

    # calculate z/L stability parameter

    z_L_list = zeff / L

    # classify into stability catagories
    # Using Foken 2008 Textbook - Table 2.9

    neutral_thresh = 0.1
    stability_class = []

    for z_L in z_L_list:

        if np.abs(z_L) < neutral_thresh:
            # neutral
            stability_class.append(0)

        else:
            if z_L < 0:
                # unstable
                stability_class.append(-1)

            else:
                # stable
                stability_class.append(1)

    return stability_class

