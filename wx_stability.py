# Beth S. 13/05/21
# Calculates stability params ustar, L from wx data files (rather than eddy covariance) for input into footprint model

import numpy as np
import netCDF4 as nc


def wx_stability_vars(wx_path, scint_path, zeff, z0_scint):
    """
    Calculates friction velocity and L from scintillometer and wx data files
    LAS daily script function 'Andreas_new'
    Parameters
    ----------
    wx_path:
    scint_path:

    Returns
    -------

    """
    # read files
    wx_ncfile = nc.Dataset(wx_path)
    scint_ncfile = nc.Dataset(scint_path)

    wx_time = wx_ncfile.variables['time']
    scint_time = scint_ncfile.variables['time']
    wx_time_dt = nc.num2date(wx_time[:], wx_time.units)
    scint_time_dt = nc.num2date(scint_time[:], scint_time.units)

    # check to see that time arrays are the same across both instruments
    if wx_time_dt.all() != scint_time_dt.all():
        raise ValueError('scint & wx time arrays are different.')

    scint_CT2 = scint_ncfile.variables['CT2']
    wx_ws = wx_ncfile.variables['WS']
    wx_tair = wx_ncfile.variables['Tair']

    scint_CT2_vals = np.array(scint_CT2[:, 0, 0, 0], dtype=np.float).tolist()
    wx_ws_vals = np.array(wx_ws[:, 0, 0, 0], dtype=np.float).tolist()
    wx_tair_vals = np.array(wx_tair[:, 0, 0, 0], dtype=np.float).tolist()
    time_vals = wx_time_dt.tolist()

    # check to see if all lists are the same length
    lists = [scint_CT2_vals, wx_ws_vals, wx_tair_vals, time_vals]
    it = iter(lists)
    the_len = len(next(it))
    if not all(len(l) == the_len for l in it):
        raise ValueError('not all lists have same length!')

    # constants
    # usign Andres 1988 constants
    c1 = 4.9
    c2 = 6.1
    c3 = 2.2

    k = 0.4  # von-karman constant
    g = 9.81  # acceleration due to gravity   (ms^-2)

    # create empty
    L_list = []
    ustar_list = []

    for a in range(0, len(time_vals)):

        # assumption: if daytime = unstable if nighttime = stable
        if 6 <= time_vals[a].hour < 16:
            L = -1  # unstable
        else:
            L = 1  # stable

        print(' ')
        print(L)

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
                fmo_unstable = c1 * (1 - c2 * (zeta)) ** (-2 / 3)

                # Tstar
                # equation 8 in Crawford et al. 2017
                tstar = - (scint_CT2_vals[a] * (zeff ** (2 / 3)) / fmo_unstable) ** 0.5

            elif L >= 0:  # stable

                if L == 0:
                    L = 0.0000000000001

                #  stability-adjusted logarithmic profile to estimate ustar
                # # original version in scint processing scripts:
                # Phi = -5 * zeta
                # Phi0 = -5 * (z0_scint / L)
                # from Grimmond and Cleugh 1994, equation 6
                Phi = - 17 * (1 - np.exp(-0.29 * zeta))
                Phi0 = - 17 * (1 - np.exp(-0.29 * (z0_scint / L)))

                # MOST  function for stable conditions
                # equation 6 in Crawford et al. 2017
                fmo_stable = c1 * (1 + (c3 * (zeta ** (2 / 3))))

                # Tstar
                # equation 8 in Crawford et al. 2017
                tstar = (scint_CT2_vals[a] * (zeff ** (2 / 3)) / fmo_stable) ** 0.5

            # ustar
            ustar = k * np.asarray(wx_ws_vals)[a] / (np.log(zeff / z0_scint) - Phi + Phi0)

            # calculate L
            # equation 7 in Crawford et al. 2017
            L = ((ustar ** 2) * (np.asarray(wx_tair_vals)[a] + 273.15)) / (g * k * tstar)

            print(L)

        L_list.append(L)
        ustar_list.append(ustar)

    wx_stability_vars = {'L': L_list, 'ustar': ustar_list}

    return wx_stability_vars
