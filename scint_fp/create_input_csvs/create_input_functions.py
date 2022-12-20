# Beth Saunders 27/05/21

# imports
import pandas as pd


def take_hourly_vars(df):
    """
    Takes dictionary of ncdf output and takes only values on the hour.
    :param df: dataframe of ncdf output
    :return: dict of values on the hour
    """

    time = df.index

    # where time is on the hour true/false
    mask = [i.minute == 0 for i in time]

    # take rows only on the hour
    hourly_df = df.loc[mask]

    return hourly_df


def find_unstable_times(df, neutral_limit=0.03):
    """

    :return:
    """

    stab_param = df['stab_param']

    # if stab_param < -neutral_limit, then unstable
    mask = [i < -neutral_limit for i in stab_param]

    # take rows only when unstable stab_param z/L
    unstable_df = df.loc[mask]

    return unstable_df


def remove_nan_rows(df):
    """

    :return:
    """

    # drop rows which have nans in important columns needed for SA model
    df_selection = df[df['wind_direction'].notna()]
    df_selection = df_selection[df['sig_v'].notna()]
    df_selection = df_selection[df['ustar'].notna()]
    df_selection = df_selection[df['L'].notna()]

    return df_selection


def time_average_sa(df, minute_resolution, period='T'):
    """

    :param df:
    :param minute_resolution:
    :return:
    """

    # construct a string to go into resample denoting the rule
    if period == 'T':
        freq_string = str(minute_resolution) + period
    else:
        freq_string = period

    # resample to minute_resolution
    resample_df = df.resample(freq_string, closed='right', label='right').mean()

    # keep track of number of samples in the average
    sample_count = df.resample(freq_string, closed='right', label='right')['v_component'].count()
    n_samples = sample_count.rename('n_samples_v_component')

    # take the variance of the output signal during the averaging period
    var_v = df.resample(freq_string, closed='right', label='right')['v_component'].var()

    # take the standard deviation
    sig_v = var_v ** (1/2)

    sig_v = sig_v.rename('sig_v')

    av_df = pd.concat([resample_df, sig_v, n_samples], axis=1)

    return av_df
