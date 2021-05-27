# Beth S. 14/05/21
# reads ec, wx and scint files
# for getting inputs for going into source area calculation program

import netCDF4 as nc
import datetime
import numpy as np

ec_path = './CSAT3_ECpack_KSSW_2016142_30min.nc'
wx_path = './Davis_BCT_2016142_15min.nc'
scint_path = './LASMkII_Fast_IMU_2016142_15min.nc'

hour_list = [3, 6, 9, 12, 15, 18, 21]

ec_ncfile = nc.Dataset(ec_path)
wx_ncfile = nc.Dataset(wx_path)
scint_ncfile = nc.Dataset(scint_path)

obs_QH_ec = ec_ncfile.variables['Q_H']
obs_sdv = ec_ncfile.variables['sd_v']
obs_ustar = ec_ncfile.variables['ustar']
obs_L = ec_ncfile.variables['L']
ec_time = ec_ncfile.variables['time']

obs_wx_wd = wx_ncfile.variables['dir']
obs_wx_ws = wx_ncfile.variables['WS']
obs_wx_time = wx_ncfile.variables['time']

obs_scint_QH = scint_ncfile.variables['Q_H']
obs_scint_time = scint_ncfile.variables['time']

# to lists
ec_time_dt = nc.num2date(ec_time[:], ec_time.units)  # convert to dt
obs_QH_ec_vals = obs_QH_ec[:, 0, 0, 0]
obs_sdv_vals = obs_sdv[:, 0, 0, 0]
obs_ustar_vals = obs_ustar[:, 0, 0, 0]
obs_L_vals = obs_L[:, 0, 0, 0]

wx_time_dt = nc.num2date(obs_wx_time[:], obs_wx_time.units)
obs_wx_wd_vals = obs_wx_wd[:, 0, 0, 0]
obs_wx_ws_vals = obs_wx_ws[:, 0, 0, 0]

scint_time_dt = nc.num2date(obs_scint_time[:], obs_scint_time.units)
obs_scint_QH_vals = obs_scint_QH[:, 0, 0, 0]

# find where it is the hour
for hour in hour_list:


    ec_time_arr = np.asarray(ec_time_dt)
    ec_time_index = np.where(ec_time_arr == datetime.datetime(2016, 5, 21, hour, 0))[0][0]

    wx_time_arr = np.asarray(wx_time_dt)
    wx_time_index = np.where(wx_time_arr == datetime.datetime(2016, 5, 21, hour, 0))[0][0]

    scint_time_arr = np.asarray(scint_time_dt)
    scint_time_index = np.where(scint_time_arr == datetime.datetime(2016, 5, 21, hour, 0))[0][0]

    qh_ec_arr = np.asarray(obs_QH_ec_vals)
    qh_ec_time = qh_ec_arr[ec_time_index]
    sdv_arr = np.asarray(obs_sdv_vals)
    sdv_time = sdv_arr[ec_time_index]
    ustar_arr = np.asarray(obs_ustar_vals)
    ustar_time = ustar_arr[ec_time_index]
    L_arr = np.asarray(obs_L_vals)
    L_time = L_arr[ec_time_index]

    wd_wx_arr = np.asarray(obs_wx_wd_vals)
    wd_wx_time = wd_wx_arr[wx_time_index]
    ws_wx_arr = np.asarray(obs_wx_ws_vals)
    ws_wx_time = ws_wx_arr[wx_time_index]

    scint_QH_arr = np.asarray(obs_scint_QH_vals)
    QH_scint_time = scint_QH_arr[scint_time_index]

    print(' ')
    print('hour: ', hour)
    print('QH scint: ', QH_scint_time)

    print('WS WX: ', ws_wx_time)
    print('WD WX: ', wd_wx_time)

    print('QH EC: ', qh_ec_time)
    print('sd v EC: ', sdv_time)
    print('ustar EC: ', ustar_time)
    print('L EC: ', L_time)




print('end')






