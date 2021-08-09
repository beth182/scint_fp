# Beth S. 13/05/21
# Calculates stability params ustar, L from wx data files (rather than eddy covariance) for input into footprint model

import scint_fp.constants as const
from scint_fp.functions import plot_functions

from scint_flux.functions import iterative_stability
from scint_flux.functions import rad_data

import numpy as np
import matplotlib.pyplot as plt
import copy


def wx_stability_vars(zeff,
                      z0_scint,
                      wx_dict,
                      scint_dict,
                      rad_dict,
                      neutral_limit=0.05):
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
    # initial_ustar = qstar_stability_estimate.calculate_initial_ustar(wx_ws_vals,
    #                                                                  zeff,
    #                                                                  z0_scint)

    # calculate values of intial L and ustar
    initial_ustar, initial_L = iterative_stability.initial_stability(df=df, ws=ws, z_effective=df['z_wx'] - df['z_d'],
                                                                     z0=df['z_0'])

    # using simple method to model QH term using Q*
    df = rad_data.simple_method_qh(df)





    # initial L calculation
    # initial_L = qstar_stability_estimate.calculate_initial_L(ustar_initial=initial_ustar,
    #                                                          QH_model=QH_model,
    #                                                          tair=wx_tair_vals,
    #                                                          press=wx_press_vals)

    # plot_functions.plot_L(initial_L, time_vals)
    # plot_functions.generic_plot_vs_time(zeff / initial_L, time_vals, 'zeff/L')

    # Iterative process

    # define acceptable differece to define when iterations stop
    ustar_threshold = 0.0001

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

                # append initial values to iteration list
                iteration_L_vals.append(L_initial)
                iteration_ustar_vals.append(ustar_initial)

            # if not the first iteration, take a copy of the previous values
            else:
                L_previous = copy.copy(L)
                ustar_previous = copy.copy(ustar)

            if L_previous == 0.0:
                L_previous = 0.0000000000001
            elif L_previous == -0.0:
                L_previous = -0.0000000000001

            # calculate stability param z/L
            stab_param = zeff / L_previous

            if stab_param < -neutral_limit:  # if unstable

                #  stability-adjusted logarithmic profile to estimate ustar
                # see equation 3 & 4 in Grimmond and Cleugh 1994
                # coefficants updated as per Foken Micromet textbook, page 61

                Phi = iterative_stability.phi_unstable(zeff / L_previous)
                Phi0 = iterative_stability.phi_unstable(z0_scint / L_previous)

                # MOST  function for unstable conditions
                # equation 5 in Crawford et al. 2017
                fmo = iterative_stability.fmo_unstable(stab_param)

                # Tstar
                # equation 8 in Crawford et al. 2017
                tstar = - iterative_stability.tstar_eq(scint_CT2_vals[a], zeff, fmo)

            elif stab_param > neutral_limit:  # stable

                #  stability-adjusted logarithmic profile to estimate ustar
                # from Grimmond and Cleugh 1994, equation 6

                Phi = iterative_stability.phi_stable(zeff / L_previous)
                Phi0 = iterative_stability.phi_stable(z0_scint / L_previous)

                # MOST  function for stable conditions
                # equation 6 in Crawford et al. 2017
                fmo = iterative_stability.fmo_stable(stab_param)

                # Tstar
                # equation 8 in Crawford et al. 2017
                tstar = iterative_stability.tstar_eq(scint_CT2_vals[a], zeff, fmo)

            elif -neutral_limit <= stab_param <= neutral_limit:
                # neutral
                Phi = 0
                Phi0 = 0

                if stab_param < 0:
                    fmo = iterative_stability.fmo_neutral_negative(stab_param)
                    tstar = - iterative_stability.tstar_eq(scint_CT2_vals[a], zeff, fmo)
                else:
                    fmo = iterative_stability.fmo_neutral_positive(stab_param)
                    tstar = iterative_stability.tstar_eq(scint_CT2_vals[a], zeff, fmo)

            if np.isnan(L_initial):
                threshold_reached = True
                ustar = np.nan
                tstar = np.nan
                L = np.nan
                fmo = np.nan
                stab_param = np.nan
            else:

                # ustar
                ustar = iterative_stability.ustar_eq(np.asarray(wx_ws_vals)[a], zeff, z0_scint, Phi, Phi0)

                # calculate L
                # equation 7 in Crawford et al. 2017
                L = iterative_stability.obukhov_length(ustar, np.asarray(wx_tair_vals)[a], tstar)

            # check to see if condition is met if we aren't on the first iteration
            if iteration_count != 0:
                if np.abs(ustar - ustar_previous) <= ustar_threshold:
                    threshold_reached = True

            if iteration_count > 50:
                threshold_reached = True
                ustar = np.nan
                L = np.nan

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
