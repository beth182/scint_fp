# Beth S. 13/05/21
# Calculates stability params ustar, L from wx data files (rather than eddy covariance) for input into footprint model

import scint_fp.constants as const
from scint_fp.functions import qstar_stability_estimate

import numpy as np
import netCDF4 as nc
import matplotlib.pyplot as plt


def wx_stability_vars(zeff,
                      z0_scint,
                      wx_dict,
                      scint_dict,
                      rad_dict):
    """
    Calculates friction velocity and L from scintillometer and wx data files
    LAS daily script function 'Andreas_new'
    :param zeff: effective beam height of path
    :param z0_scint: roughness length estimation
    :param wx_dict: dictionary of hourly values from wx station
    :param scint_dict: dictionary hourly values from scint
    :param rad_dict: dictionary of hourly values from radiometer
    :return:
    """

    # check to see that time arrays are the same across both instruments
    if wx_dict['time'].all() != scint_dict['time'].all() != rad_dict['time'].all():
        raise ValueError('scint, wx & rad time arrays are different.')

    time_vals = wx_dict['time']

    wx_ws_vals = wx_dict['WS']
    wx_tair_vals = wx_dict['Tair']
    wx_press_vals = wx_dict['press']

    scint_CT2_vals = scint_dict['CT2']

    rad_qstar_vals = rad_dict['Qstar']

    # check to see if all lists are the same length
    lists = [scint_CT2_vals, wx_ws_vals, wx_tair_vals, time_vals, rad_qstar_vals]
    it = iter(lists)
    the_len = len(next(it))
    if not all(len(l) == the_len for l in it):
        raise ValueError('not all lists have same length!')

    # create empty
    L_list = []
    ustar_list = []

    # calculate values of intial L and ustar
    # calculate initial ustar (take equation for neutral conditions)
    initial_ustar = qstar_stability_estimate.calculate_initial_ustar(wx_ws_vals,
                                                     zeff,
                                                     z0_scint)

    # using simple method to model QH term using Q*
    QH_model = qstar_stability_estimate.simple_method_qh(rad_dict)

    # initial L calculation
    initial_L = qstar_stability_estimate.calculate_initial_L(ustar_initial=initial_ustar,
                                                             QH_model=QH_model,
                                                             tair=wx_tair_vals,
                                                             press=wx_press_vals)

    for a in range(0, len(time_vals)):

        L = initial_L[a]
        # stability parameter
        zeta = zeff / L

        for i in range(0, 20):
            if L < 0:  # if unstable

                #  stability-adjusted logarithmic profile to estimate ustar
                # see equation 3 & 4 in Grimmond and Cleugh 1994
                # coefficants updated as per Foken Micromet textbook, page 61
                x = (-19.3 * zeta + 1) ** 0.25  # 1994 paper = -16, Foken = -19.3
                x0 = (-19.3 * (z0_scint / L) + 1) ** 0.25
                Phi = 2 * np.log((x + 1) / 2) + np.log(((x ** 2) + 1) / 2) - 2 * np.arctan(x) + np.pi / 2
                Phi0 = 2 * np.log((x0 + 1) / 2) + np.log((x0 ** 2 + 1) / 2) - 2 * np.arctan(x0) + np.pi / 2

                # MOST  function for unstable conditions
                # equation 5 in Crawford et al. 2017
                fmo_unstable = const.c1 * (1 - const.c2 * (zeta)) ** (-2 / 3)

                # Tstar
                # equation 8 in Crawford et al. 2017
                tstar = - (scint_CT2_vals[a] * (zeff ** (2 / 3)) / fmo_unstable) ** 0.5

            elif L >= 0:  # stable

                if L == 0:
                    L = 0.0000000000001

                #  stability-adjusted logarithmic profile to estimate ustar
                # # original version in scint processing scint_fp:
                # Phi = -5 * zeta
                # Phi0 = -5 * (z0_scint / L)
                # from Grimmond and Cleugh 1994, equation 6
                Phi = - 17 * (1 - np.exp(-0.29 * zeta))
                Phi0 = - 17 * (1 - np.exp(-0.29 * (z0_scint / L)))

                # MOST  function for stable conditions
                # equation 6 in Crawford et al. 2017
                fmo_stable = const.c1 * (1 + (const.c3 * (zeta ** (2 / 3))))

                # Tstar
                # equation 8 in Crawford et al. 2017
                tstar = (scint_CT2_vals[a] * (zeff ** (2 / 3)) / fmo_stable) ** 0.5

            # ustar
            ustar = const.k * np.asarray(wx_ws_vals)[a] / (np.log(zeff / z0_scint) - Phi + Phi0)

            # calculate L
            # equation 7 in Crawford et al. 2017
            L = ((ustar ** 2) * (np.asarray(wx_tair_vals)[a] + const.kelv)) / (const.g * const.k * tstar)


        L_list.append(L)
        ustar_list.append(ustar)

    wx_stability_vars = {'L': L_list, 'ustar': ustar_list}

    return wx_stability_vars
