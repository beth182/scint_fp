# Beth S. 14/05/21
# Gets u & v components of wind from ws and dir from met data files
# to be put into source area calculation program

import numpy as np
import pandas as pd


def ws_wd_to_u_v(ws_series, wd_series):
    """
    Get u and v components from WS & dir, observed by WX station.
    :param ws_series: wind speed series. Time as index optional
    :param wd_series: wind direction series. Time as index optional
    :return: u and v components of wind as a dataframe
    """

    wd_rad = np.radians(wd_series)

    u = - np.abs(ws_series) * np.sin(wd_rad)
    v = - np.abs(ws_series) * np.cos(wd_rad)

    u_series = u.rename('u_component')
    v_series = v.rename('v_component')

    # combine series with existing wx dataframe
    component_df = pd.concat([u_series, v_series], axis=1)

    return component_df


def u_v_to_ws_wd(u_series, v_series):
    """
    Get WS & dir from u & v components of wind
    :param u_series:
    :param v_series:
    :return:
    """

    # wind speed
    WS = (u_series ** 2 + v_series ** 2) ** 0.5

    # https://confluence.ecmwf.int/pages/viewpage.action?pageId=133262398
    WD = 180 + (180 / np.pi) * np.arctan2(u_series, v_series)
    WD[np.where(WD < 0)[0]] += 360

    WS = WS.rename('wind_speed_convert')
    WD = WD.rename('wind_direction_convert')

    wind_df = pd.concat([WS, WD], axis=1)

    return wind_df


"""
# an example script - to prove giving ws & wd, converting to u & v, and then converting back - yields the same vals
# create arbitrary wind vals
ws = [1., 5., 10., 5., 1.]
wd = [100., 200., 100., 350., 50.]

# convert to df
pd_dict = {'ws': ws, 'wd': wd}
wind_df = pd.DataFrame(pd_dict)

# convert ws & dir to u and v using function ws_wd_to_u_v
u_v_df = ws_wd_to_u_v(wind_df['ws'], wind_df['wd'])

# convert this u & v back to ws and dir using function u_v_to_ws_wd
ws_dir_con = u_v_to_ws_wd(u_v_df['u_component'], u_v_df['v_component'])

# check they are the same
assert ws_dir_con['wind_speed_convert'].all() == wind_df['ws'].all()
assert ws_dir_con['wind_direction_convert'].all() == wind_df['wd'].all()
"""


def std_v(df):
    """
    Calculates the standard deviation of the v component of wind
    currently unused - check time_average_sa_input for the sigv calculation
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
