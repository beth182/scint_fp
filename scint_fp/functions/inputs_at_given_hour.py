# Beth Saunders 27/05/21
# selects a set of inputs at a given hour from whole day of inputs

# imports
import numpy as np

def inputs_for_given_hour(hour_choice, hour_inputs):
    """
    Stes a combination of 1 hour's representative met-input values
    Parameters
    ----------
    hour_choice: int representing hour chosen
    hour_inputs: dictionary of whole day's inputs

    Returns
    -------
    Dictionary of inputs for 1 hour
    """

    i = np.where([i.hour == hour_choice for i in hour_inputs['time']])

    time = hour_inputs['time'][i][0]
    sigv = hour_inputs['sigv'][i][0]
    wd = hour_inputs['wd'][i][0]
    L = hour_inputs['L'][i][0]
    ustar = hour_inputs['ustar'][i][0]

    hour_met_inputs = {'time': time, 'sigv': sigv, 'wd': wd, 'L': L, 'ustar': ustar}

    return hour_met_inputs