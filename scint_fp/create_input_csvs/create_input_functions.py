# Beth Saunders 27/05/21


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
