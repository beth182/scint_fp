# Beth Saunders 25/05/21
# take an initial guess of stability using net all-wave radiation

# imports

import scint_fp.constants as const

import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt


def simple_method_qh(rad_dict):
    """
    Calculates a model of the QH term to go into L equation
    following following Grimmond and Cleugh
    all equation numbers reference this paper
    :param rad_dict: dictionary of hourly output from the radiometer
    :return: model of the QH term
    """

    time = rad_dict['time']
    qstar = rad_dict['Qstar']

    # check hourly time and qstar arrays are the same len
    assert len(time) == len(qstar)

    # index of first hour where qstar > 20
    index_at_condition = np.where(qstar > 20)[0][0]

    if index_at_condition == 0:
        raise ValueError('index_at_condition is 0, so cannot get preceeding index')

    # index of hour preceeding qstar > 20
    index_preceeding_condition = index_at_condition - 1

    # find t
    # t = 0 for hour preceeding qstar > 20
    # t = 1 for the first hour when qstar > 20
    # t = 2 is the second hour when qstar > 20
    # carry on for each hour after qstar > 20
    t = []
    count = 1
    for i in range(0, len(qstar)):

        if i <= index_preceeding_condition:
            t.append(0)
        else:

            if qstar[i] > 20:
                t.append(count)
                count += 1
            else:
                t.append(0)

    # find T
    # T = number of hours in the day where qstar > 20
    T = len(np.where(qstar > 20)[0])

    # equation 7a
    x = 0.232 * np.exp(0.847 * (np.asarray(t) / T))

    # find where qstar < -20 (night)
    index_night = np.where(qstar < -20)[0]
    # equation 7b
    x[index_night] = 0.1

    QH_model = qstar * x

    return QH_model

    # plt.scatter(time, qstar)
    # plt.xlabel('time')
    # plt.ylabel('Q*')
    # plt.gcf().autofmt_xdate()
    #
    # plt.scatter(time, x)
    # plt.xlabel('time')
    # plt.ylabel('x')
    # plt.gcf().autofmt_xdate()
    #
    # plt.scatter(time, QH_model)
    # plt.xlabel('time')
    # plt.ylabel('QH_model')
    # plt.gcf().autofmt_xdate()


def calculate_initial_ustar(ws,
                            zeff,
                            z0_scint):
    """
    Makes a initial estimate of friction to go into iterative process.
    For neutral conditions - so does use a similarity function for momentum

    Parameters
    ----------
    wx_ws_vals: wind speed array
    zeff: effective measuremtn height of scintillometer path
    z0_scint: roughness length of area around scintillometer path

    Returns
    -------
    ustar_initial: Initial estimate of friction velocity
    """

    ustar_initial = const.k * np.asarray(ws) / np.log(zeff / z0_scint)

    return ustar_initial


def calculate_initial_L(ustar_initial,
                        QH_model,
                        tair,
                        press):
    """
    Makes an initial estimate of Obukhov length
    Using Simple method for estimation (Sue & Cleugh 1994) which replaces the QH term
    Parameters
    ----------
    ustar_initial: initial estimate of friction velocity.
    QH_model: "modelled" QH from the simple method array
    tair: air temperature array
    press: pressure array

    Returns
    -------
    L_initial: initial estimate of Obukhov length
    """

    rho = np.asarray(press) / (const.R * (np.asarray(tair) + const.kelv))
    L_initial = - ((ustar_initial ** 3) * rho * const.cp * (np.asarray(tair) + const.kelv)) / (const.k * const.g * QH_model)

    return L_initial
