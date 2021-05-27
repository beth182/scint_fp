# Beth S. 14/05/21
# Gets u & v components of wind from ws and dir from met data files
# to be put into source area calculation program

import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import math
import datetime
from matplotlib.dates import DateFormatter


def wind_components(nc_file_path):
    """
    Get u and v components from WS & dir, observed by WX station.
    Returns
    -------

    """

    wx_ncfile = nc.Dataset(nc_file_path)
    obs_wx_wd = wx_ncfile.variables['dir']
    obs_wx_ws = wx_ncfile.variables['WS']
    obs_wx_time = wx_ncfile.variables['time']

    obs_wx_wd_vals = obs_wx_wd[:, 0, 0, 0]
    obs_wx_ws_vals = obs_wx_ws[:, 0, 0, 0]
    wx_time_dt = nc.num2date(obs_wx_time[:], obs_wx_time.units)

    u_vals = []
    v_vals = []

    for i in range(0, len(wx_time_dt)):
        ws = obs_wx_ws_vals[i]
        wd = obs_wx_wd_vals[i]

        wd_rad = math.radians(wd)

        u = - np.abs(ws) * np.sin(wd_rad)
        v = - np.abs(ws) * np.cos(wd_rad)

        u_vals.append(u)
        v_vals.append(v)

    wind_components = {'u': u_vals, 'v': v_vals, 'time': wx_time_dt, 'ws': obs_wx_ws_vals, 'wd': obs_wx_wd_vals}

    return wind_components


def plot_wind_components(wind_components):
    """
    Plot u and v components of wind
    Returns
    -------

    """

    wx_time_dt = wind_components['time']
    u_vals = wind_components['u']
    v_vals = wind_components['v']
    obs_wx_ws_vals = wind_components['ws']
    obs_wx_wd_vals = wind_components['wd']

    fig, ax = plt.subplots()

    ax.plot(wx_time_dt.tolist(), u_vals, alpha=0.2, color='blue')
    ax.scatter(wx_time_dt.tolist(), u_vals, label='u', marker='^', color='blue')

    ax.plot(wx_time_dt.tolist(), v_vals, alpha=0.2, color='orange')
    ax.scatter(wx_time_dt.tolist(), v_vals, label='v', marker='v', color='orange')

    ax.plot(wx_time_dt.tolist(), obs_wx_ws_vals, label='ws', linestyle='None', marker='x', color='red')

    ax2 = ax.twinx()
    ax2.plot(wx_time_dt.tolist(), obs_wx_wd_vals, label='dir', linestyle='None', marker='.', color='green')

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


def get_wd_dir(nc_file_path_15min):
    """
    Get wind direction from 15 minute sample files.
    Parameters
    ----------
    nc_file_path_15min: file path to wx data file - 15 min sample.

    Returns
    -------

    """
    wx_ncfile = nc.Dataset(nc_file_path_15min)
    obs_wx_wd = wx_ncfile.variables['dir']
    obs_wx_time = wx_ncfile.variables['time']

    obs_wx_wd_vals = obs_wx_wd[:, 0, 0, 0]
    wx_time_dt = nc.num2date(obs_wx_time[:], obs_wx_time.units)

    wind_dir = {'time': wx_time_dt, 'dir': obs_wx_wd_vals}

    return wind_dir

