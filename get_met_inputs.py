# Beth S. 14/05/21
# Get all met inputs for fp calculation.

import wx_u_v_components
import scintools as sct
import estimate_z0
import wx_stability
import matplotlib.pyplot as plt
import numpy as np


def get_fp_met_inputs(wx_file_path_15min,
                      wx_file_path_1min,
                      scint_path,
                      zeff,
                      z0_scint):
    """
    Get ustar, wind dir, L, std v values from wx data and scint data
    Returns
    -------

    """

    u_v = wx_u_v_components.wind_components(wx_file_path_1min)
    # plot_wind_components(u_v)

    v_vals = u_v['v']
    v_vals_15_min = [v_vals[i:i + 15] for i in range(0, len(v_vals), 15)]

    sigma_v = wx_u_v_components.std_v(v_vals_15_min)
    get_wind = wx_u_v_components.get_wd_dir(wx_file_path_15min)
    time = get_wind['time']
    wind_dir = get_wind['dir']

    stability_vars = wx_stability.wx_stability_vars(wx_file_path_15min, scint_path, zeff, z0_scint)

    L_vals = stability_vars['L']
    ustar_vals = stability_vars['ustar']

    met_inputs_fp = {'sigv': sigma_v, 'wd': wind_dir, 'L': L_vals, 'ustar': ustar_vals, 'time': time}

    return met_inputs_fp


def inputs_for_hour(met_inputs_fp):
    """
    Function to return all needed input params for footprint calculation for every hour studied
    Returns
    -------

    """

    time = met_inputs_fp['time']
    wd = met_inputs_fp['wd']
    L = np.asarray(met_inputs_fp['L'])
    ustar = np.asarray(met_inputs_fp['ustar'])
    sigv = np.asarray(met_inputs_fp['sigv'])

    # index of where time is on the hour
    hour_index = np.where([i.minute == 0 for i in time])

    time_hour = time[hour_index]
    wd_hour = wd[hour_index]
    L_hour = L[hour_index]
    ustar_hour = ustar[hour_index]
    sigv_hour = sigv[hour_index]

    hour_vals = {'time': time_hour, 'wd': wd_hour, 'L': L_hour, 'ustar': ustar_hour, 'sigv': sigv_hour}

    return hour_vals


