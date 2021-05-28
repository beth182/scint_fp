# Beth S. 13/05/21
# Calculates stability params ustar, L from wx data files (rather than eddy covariance) for input into footprint model

import scint_fp.constants as const
from scint_fp.functions import qstar_stability_estimate
from scint_fp.functions import plot_functions

import numpy as np
import matplotlib.pyplot as plt
import copy


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
    iteration_count_list = []
    iteration_dict_L = {}
    iteration_dict_ustar = {}

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

    # plot_functions.plot_L(initial_L, time_vals)
    # plot_functions.generic_plot_vs_time(zeff / initial_L, time_vals, 'zeff/L')

    # Iterative process

    # define acceptable differece to define when iterations stop
    ustar_threshold = 0.001

    # for each time
    for a in range(0, len(time_vals)):

        # get hour as string for key to dict
        hour = time_vals[a].strftime('%H')

        # setting a condition to break loop as initially False
        # will keep looping until the difference in ustar output is smaller than ustar_threshold
        threshold_reached = False

        # define initial stability
        L_initial = initial_L[a]
        ustar_initial = initial_ustar[a]

        # counter to log how many iterations we've gone through
        iteration_count = 0

        # define list where all values from iterations are stored
        iteration_L_vals = []
        iteration_ustar_vals = []

        # while the condition has not be satisfied
        while not threshold_reached:

            # for the first iteration, take L initial as L
            if iteration_count == 0:
                L_previous = copy.copy(L_initial)
                ustar_previous = copy.copy(ustar_initial)
            # if not the first iteration, take a copy of the previous values
            else:
                L_previous = copy.copy(L)
                ustar_previous = copy.copy(ustar)

            # stability parameter
            zeta = zeff / L_previous

            if L_previous < 0:  # if unstable

                #  stability-adjusted logarithmic profile to estimate ustar
                # see equation 3 & 4 in Grimmond and Cleugh 1994
                # coefficants updated as per Foken Micromet textbook, page 61
                x = (-19.3 * zeta + 1) ** 0.25  # 1994 paper = -16, Foken = -19.3
                x0 = (-19.3 * (z0_scint / L_previous) + 1) ** 0.25
                Phi = 2 * np.log((x + 1) / 2) + np.log(((x ** 2) + 1) / 2) - 2 * np.arctan(x) + np.pi / 2
                Phi0 = 2 * np.log((x0 + 1) / 2) + np.log((x0 ** 2 + 1) / 2) - 2 * np.arctan(x0) + np.pi / 2

                # MOST  function for unstable conditions
                # equation 5 in Crawford et al. 2017
                fmo_unstable = const.c1 * (1 - const.c2 * (zeta)) ** (-2 / 3)

                # Tstar
                # equation 8 in Crawford et al. 2017
                tstar = - (scint_CT2_vals[a] * (zeff ** (2 / 3)) / fmo_unstable) ** 0.5

            elif L_previous >= 0:  # stable

                if L_previous == 0:
                    L_previous = 0.0000000000001

                #  stability-adjusted logarithmic profile to estimate ustar
                # # original version in scint processing scint_fp:
                # Phi = -5 * zeta
                # Phi0 = -5 * (z0_scint / L)
                # from Grimmond and Cleugh 1994, equation 6
                Phi = - 17 * (1 - np.exp(-0.29 * zeta))
                Phi0 = - 17 * (1 - np.exp(-0.29 * (z0_scint / L_previous)))

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

            # check to see if condition is met if we aren't on the first iteration
            if iteration_count != 0:
                if np.abs(ustar - ustar_previous) <= ustar_threshold:
                    threshold_reached = True

            iteration_count += 1
            iteration_L_vals.append(L)
            iteration_ustar_vals.append(ustar)

        # append each hour's L and ustar to lists
        iteration_count_list.append(iteration_count)
        iteration_dict_L[hour] = iteration_L_vals
        iteration_dict_ustar[hour] = iteration_ustar_vals
        L_list.append(L)
        ustar_list.append(ustar)

    wx_stability_vars = {'L': np.asarray(L_list),
                         'ustar': np.asarray(ustar_list),
                         'iteration_count': np.asarray(iteration_count_list),
                         'iterations_L': iteration_dict_L,
                         'iterations_ustar': iteration_dict_ustar
                         }

    return wx_stability_vars
