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
