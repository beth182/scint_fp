# Beth S. 14/05/21
# Gets u & v components of wind from ws and dir from met data files
# to be put into source area calculation program

import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import math
import datetime
from matplotlib.dates import DateFormatter


def wind_components(time,
                    ws_array,
                    wd_array):
    """
    Get u and v components from WS & dir, observed by WX station.
    :param time: time array
    :param ws: wind speed array
    :param wd: wind direction array
    :return: u and v components of wind
    """

    u_vals = []
    v_vals = []

    for i in range(0, len(time)):
        ws = ws_array[i]
        wd = wd_array[i]

        wd_rad = math.radians(wd)

        u = - np.abs(ws) * np.sin(wd_rad)
        v = - np.abs(ws) * np.cos(wd_rad)

        u_vals.append(u)
        v_vals.append(v)

    wind_components = {'u': u_vals, 'v': v_vals}

    return wind_components


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


def std_v(v_vals_15_min):
    """
    Caculate the standard deviation of the v componant of wind
    Parameters
    ----------
    v_vals: v componant of wind

    Returns
    -------

    """
    std_v_list = []

    for sample in v_vals_15_min:
        std_v = np.std(sample)
        std_v_list.append(std_v)

    return std_v_list


