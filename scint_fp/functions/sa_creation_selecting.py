

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





    print('end')