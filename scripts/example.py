

scint_path = './LASMkII_Fast_IMU_2016142_15min.nc'
scint_ncfile = nc.Dataset(scint_path)
obs_scint_QH = scint_ncfile.variables['Q_H']
obs_scint_time = scint_ncfile.variables['time']

scint_time_dt = nc.num2date(obs_scint_time[:], obs_scint_time.units)
obs_scint_QH_vals = obs_scint_QH[:, 0, 0, 0]