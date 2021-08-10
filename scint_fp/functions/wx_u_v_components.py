# Beth S. 14/05/21
# Gets u & v components of wind from ws and dir from met data files
# to be put into source area calculation program

import numpy as np
import math
import pandas as pd


def wind_components(df):
    """
    Get u and v components from WS & dir, observed by WX station.
    :param time: time array
    :param ws: wind speed array
    :param wd: wind direction array
    :return: u and v components of wind
    """

    time = df.index,
    ws_array = df['wind_speed_adj']
    wd_array = df['wind_direction']

    wd_rad = np.radians(wd_array)

    u = - np.abs(ws_array) * np.sin(wd_rad)
    v = - np.abs(ws_array) * np.cos(wd_rad)

    u_series = u.rename('u_component')
    v_series = v.rename('v_component')

    # combine series with existing wx dataframe
    updated_wx_df = pd.concat([df, u_series, v_series], axis=1)

    return updated_wx_df


def std_v(df):
    """
    Calculates the standard deviation of the v component of wind
    Parameters
    ----------
    wind_components: dictionary for components of wind at 1 min

    Returns
    -------
    Dictonary of on-the-hour standard deviation of v component of wind
    """

    v_1min = df['v_component']
    time_1min = df.index

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

    sigv_df = pd.DataFrame(sigv_dict)
    sigv_df = sigv_df.set_index('time')

    return sigv_df


