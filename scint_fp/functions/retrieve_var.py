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
