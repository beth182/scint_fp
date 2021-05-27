# Beth Saunders 27/05/21
# read var from netcdf

import netCDF4 as nc
import numpy as np


def retrive_var(file_path,
                var_names):
    """
    Retrive variable from ncdf file
    :param file_path: sting of ncdf filepath
    :param var_names: LIST of strings; variable names as they appear in ncdf file
    :return: Dict of both time (as array of datetime objects) & variable array
    """

    ncdf_file = nc.Dataset(file_path)

    file_time = ncdf_file.variables['time']
    time_dt = nc.num2date(file_time[:], file_time.units)

    var_dict = {'time': time_dt}

    for var_name in var_names:
        file_var = ncdf_file.variables[var_name]
        var_array = np.array(file_var[:, 0, 0, 0], dtype=np.float)
        var_dict[var_name] = var_array

    return var_dict


def take_hourly_vars(var_dict):
    """
    Takes dictionary of ncdf output and takes only values on the hour.
    :param var_dict: dictionary of ncdf output
    :return: dict of values on the hour
    """

    time = var_dict['time']

    # index of where time is on the hour
    hour_index = np.where([i.minute == 0 for i in time])

    hourly_dict = {}

    for key in var_dict.keys():
        hourly_vals = var_dict[key][hour_index]
        hourly_dict[key] = hourly_vals

    return hourly_dict

