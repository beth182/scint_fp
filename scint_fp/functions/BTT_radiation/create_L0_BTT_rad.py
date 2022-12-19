# 5s time resolution (or anything bellow 1 min) BTT files do nit exist - like they do for KSSW
# This file aims to create them

import datetime as dt
import pandas as pd
import numpy as np

from scint_flux.functions import find_files
from scint_flux.functions import write_ncdf

# USER INPUTS
########################################################################################################################
# give a range of DOYs to run for
DOY_start = 2017001
DOY_stop = 2017365

site = 'BTT'

instrument = 'CNR4'

########################################################################################################################
# currently start year has to be the same as stop year
DOY_start_year = str(DOY_start)[0:4]
DOY_stop_year = str(DOY_stop)[0:4]

assert DOY_start_year == DOY_stop_year

DOY_start_day = int(str(DOY_start)[4:])
DOY_stop_day = int(str(DOY_stop)[4:])

DOY_list = []
for i in range(DOY_start_day, DOY_stop_day + 1):
    DOY_construct = int(DOY_start_year + str(i).zfill(3))
    DOY_list.append(DOY_construct)

for DOYyear in DOY_list:

    print(DOYyear)
    print(' ')

    # find raw file
    # construct datetime object
    datetime_obj = dt.datetime.strptime(str(DOYyear), '%Y%j')

    # test with L0 15-min file
    """
    import netCDF4 as nc
    L0_filepath = find_files.find_file(datetime_obj, site, instrument, 'L0',
                                        '//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_raw/', time_res='15min')
    nc_set = nc.Dataset(L0_filepath)
    l0_time = nc_set.variables['time']
    l0_time_dt = nc.num2date(l0_time[:], l0_time.units)
    l0_kdn = nc_set.variables['Kdn'][:,0,0,0]
    l0_kup = nc_set.variables['Kup'][:,0,0,0]
    l0_ldn = nc_set.variables['Ldn'][:,0,0,0]
    l0_lup = nc_set.variables['Lup'][:,0,0,0]
    l0_qstar = nc_set.variables['Qstar'][:, 0, 0, 0]
    nc_dict = {'Kdn': l0_kdn, 'Kup': l0_kup, 'Ldn': l0_ldn, 'Lup': l0_lup, 'time': l0_time_dt, 'Qstar': l0_qstar}
    l0_df = pd.DataFrame.from_dict(nc_dict)
    l0_df = l0_df.set_index('time')
    """

    # construct filepath
    raw_filepath = find_files.find_file(datetime_obj, site, instrument, 'raw',
                                        '//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_raw/')

    if raw_filepath:
        pass
    else:
        continue

    # read raw file
    df = pd.read_csv(raw_filepath, header=None)

    # get time index
    df['time'] = pd.to_datetime(df[0], format='%Y-%m-%d %H:%M:%S')
    df = df.set_index('time')

    # specify column names
    df = df.rename(columns={2: 'Kdn', 3: 'Kup', 4: 'Ldn', 5: 'Lup'})

    # drop uneeded columns
    df = df.drop([0, 1], axis=1)

    # get Qstar
    df['Qstar'] = df['Kdn'] - df['Kup'] + df['Ldn'] - df['Lup']

    # make sure there are no duplicate rows
    assert len(np.where(df.index.duplicated())[0]) == 0

    # resample pd df to 1-minute
    # rm last entry - as midnight the next day
    df_resample = df.resample('1T', closed='right', label='right').mean()[:-1]

    # save as nc file
    write_ncdf.write_file(df_resample, site, 'L0', '1min', instrument)

print('end')


