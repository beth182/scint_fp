import pandas as pd


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

