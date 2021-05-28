# Beth S. 14/05/21
# Gets u & v components of wind from ws and dir from met data files
# to be put into source area calculation program

import numpy as np
import math


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

    wind_components = {'u': u_vals, 'v': v_vals, 'time': time}

    return wind_components


def std_v(wind_components):
    """
    Calculates the standard deviation of the v component of wind
    Parameters
    ----------
    wind_components: dictionary for components of wind at 1 min

    Returns
    -------
    Dictonary of on-the-hour standard deviation of v component of wind
    """

    v_1min = wind_components['v']
    time_1min = wind_components['time']

    # group 1-min observation into groups of 60
    v_groups = [v_1min[i:i + 60] for i in range(0, len(v_1min), 60)]

    time_groups = [time_1min[i:i + 60] for i in range(0, len(time_1min), 60)]
    time = []
    for group in time_groups:
        time.append(group[-1])

    std_v_list = []

    for sample in v_groups:
        std_v = np.std(sample)
        std_v_list.append(std_v)

    sigv_dict = {'sigv': np.asarray(std_v_list), 'time': np.asarray(time)}

    return sigv_dict


