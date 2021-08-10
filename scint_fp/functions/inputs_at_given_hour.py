# Beth Saunders 27/05/21
# selects a set of inputs at a given hour from whole day of inputs

# imports
import numpy as np


def inputs_for_given_hour(hour_choice, hour_df):
    """
    Finds a combination of 1 hour's representative met-input values
    Parameters
    ----------
    hour_choice: int representing hour chosen
    hour_df: dataframe of whole day's inputs

    Returns
    -------
    Dataframe of inputs for 1 hour
    """

    i = np.where([i.hour == hour_choice for i in hour_df.index])
    row = hour_df.iloc[i]

    return row