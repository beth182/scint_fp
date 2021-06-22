# Beth Saunders 27/05/21
# creates footprint of observation

import scintools as sct
from scint_fp.functions import estimate_z0, wx_u_v_components, retrieve_var, wx_stability, \
    inputs_at_given_hour, plot_functions

import numpy as np
import copy
import matplotlib.pyplot as plt
import pandas as pd

out_dir = 'C:/Users/beths/Desktop/LANDING/fp_raster_tests/'

# files should be WX from new_scint_data, L2
# and scint data from new_scint_data, L1
wx_file_path_15min = '../example_data/ncdf/Davis_BCT_2016142_15min_newdata_L2.nc'
wx_file_path_1min = '../example_data/ncdf/Davis_BCT_2016142_1min_newdata_L2.nc'
scint_path = '../example_data/ncdf/LASMkII_Fast_IMU_2016142_15min_newdata_L1.nc'
rad_file = '../example_data/ncdf/CNR4_KSSW_2016142_15min.nc'

# bdsm_path = 'D:/Documents/large_rasters/clipped/20_m_resample/resample_20_surface.tif'
# cdsm_path = 'D:/Documents/large_rasters/clipped/20_m_resample/resample_20_veg.tif'
# dem_path = 'D:/Documents/large_rasters/clipped/20_m_resample/resample_20_terrain.tif'

bdsm_path = 'D:/Documents/large_rasters/clipped/10_m_resampled/resample_10_surface.tif'
cdsm_path = 'D:/Documents/large_rasters/clipped/10_m_resampled/resample_10_veg.tif'
dem_path = 'D:/Documents/large_rasters/clipped/10_m_resampled/resample_10_terrain.tif'



# define scint pair
# path 12 - BCT -> IMU
pair_raw = sct.ScintillometerPair(x=[285440.6056, 284562.3107],
                                  y=[5712253.017, 5712935.032],
                                  z_asl=[142, 88],
                                  pair_id='BCT_IMU',
                                  crs='epsg:32631')

pair = copy.deepcopy(pair_raw)

roughness_inputs = sct.RoughnessInputs()

point_res = 50
weightings = (100, 200)
path_params = {'point_res': point_res,
               'weightings': weightings}

spatial_inputs = sct.SpatialInputs(
    domain_size=65000,
    x=float(pair.path_center().x),
    y=float(pair.path_center().y),
    z_asl=pair.path_center_z(),
    bdsm_path=bdsm_path,
    cdsm_path=cdsm_path,
    dem_path=dem_path)

path_transect = pair.path_transect(dsm_file=spatial_inputs.bdsm_path, point_res=10)

# get effective beam height
zeff = path_transect.effective_beam_height()

########################################################################################################################
# get estimate of z0 using estimate_z0
z0_scint = estimate_z0.calculate_quick_z0(spatial_inputs, crop_size=200)['z_0']

# retrieve variables needed
# WX station 15-min file
# temperature, pressure, wind speed, wind direction
WX_15min = retrieve_var.retrive_var(wx_file_path_15min,
                                    ['Tair', 'press', 'WS', 'dir'])
# WX station 1-min file
# wind speed, wind direction
WX_1min = retrieve_var.retrive_var(wx_file_path_1min,
                                   ['WS', 'dir'])
# scint 15-min file
# temperature structure parameter
scint_15min = retrieve_var.retrive_var(scint_path, ['CT2'])
# radiation 15-minute file
# net all-wave raditation
rad_15min = retrieve_var.retrive_var(rad_file,
                                     ['Qstar'])

# wind calculations
u_v = wx_u_v_components.wind_components(time=WX_1min['time'],
                                        ws_array=WX_1min['WS'],
                                        wd_array=WX_1min['dir'])

# plot wind direction
# plot_functions.generic_plot_vs_time(var=WX_15min['dir'], time=WX_15min['time'], varname='Wind direction')

# optional plotting of components
# plot_functions.plot_wind_components(time=WX_1min['time'],
#                                        ws=WX_1min['WS'],
#                                        wd=WX_1min['dir'],
#                                        wind_components=u_v)

# standard deviation of v component of wind
sigma_v = wx_u_v_components.std_v(u_v)

# get only hourly values
WX_hourly = retrieve_var.take_hourly_vars(WX_15min)
scint_hourly = retrieve_var.take_hourly_vars(scint_15min)
rad_hourly = retrieve_var.take_hourly_vars(rad_15min)

# get stability vars
stability_vars = wx_stability.wx_stability_vars(zeff=zeff,
                                                z0_scint=z0_scint,
                                                wx_dict=WX_hourly,
                                                scint_dict=scint_hourly,
                                                rad_dict=rad_hourly)

# iteration plots
# plot_functions.stability_iteration_plots(stability_vars, out_dir + 'stability_iterations/')
plt.close('all')

hour_inputs = {'wd': WX_hourly['dir'],
               'sigv': sigma_v['sigv'],
               'L': stability_vars['L'],
               'ustar': stability_vars['ustar'],
               'time': WX_hourly['time']}

# stability_class = plot_functions.classify_stability(hour_inputs['time'], zeff, hour_inputs['L'])
# plot_functions.generic_plot_vs_time(zeff / hour_inputs['L'], hour_inputs['time'], 'zeff/L', stability_class)
# plot_functions.generic_plot_vs_time(hour_inputs['wd'], hour_inputs['time'], 'Wind Direction ($^{\circ}$)', stability_class)
# plot_functions.generic_plot_vs_time(hour_inputs['sigv'], hour_inputs['time'], '$\sigma$v (m s$^{-1}$)', stability_class)
# plot_functions.generic_plot_vs_time(hour_inputs['ustar'], hour_inputs['time'], 'u$_{*}$ (m s$^{-1}$)', stability_class)
# plot_functions.plot_L(hour_inputs['L'], hour_inputs['time'], stability_class)

# save as table
df = pd.DataFrame.from_dict(hour_inputs)
col_order = ['time', 'wd', 'sigv', 'ustar', 'L']
df[col_order].to_csv(out_dir + 'met_inputs.csv')

# find rows where any items in the dataframe are nans
nan_hours_df = df[df.isna().any(axis=1)]['time'].apply(lambda x: x.strftime('%H'))
nan_hours = list(map(int, nan_hours_df))
all_possible_hours = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 0]
# hours_valid = [x for x in all_possible_hours if x not in nan_hours]

hours_valid = [22, 23, 0]

# create footprints
for hour in hours_valid:
    hour_met_inputs = inputs_at_given_hour.inputs_for_given_hour(hour, hour_inputs)

    time = hour_met_inputs['time']
    sigv = hour_met_inputs['sigv']
    wd = hour_met_inputs['wd']
    L = hour_met_inputs['L']
    ustar = hour_met_inputs['ustar']

    title_string = time.strftime('%Y') + '_' + time.strftime('%j') + '_' + time.strftime('%H')

    met_inputs = sct.MetInputs(obukhov=L,
                               sigv=sigv,
                               ustar=ustar,
                               wind_dir=wd
                               )

    fp_path = sct.run_footprintpath(scint_pair=pair,
                                    met_inputs=met_inputs,
                                    roughness_inputs=roughness_inputs,
                                    path_params=path_params,
                                    spatial_inputs=spatial_inputs)

    fp_path.footprint[fp_path.footprint == 0.0] = np.nan

    string_to_save = str(pair.pair_id) + '_' + str(spatial_inputs.domain_size) + '_' + title_string
    file_out = out_dir + 'hourly/' + string_to_save + '.tif'
    fp_path.save_tiff(file_out)

    print(title_string)

print('end')

# save path points
# fp_path.path_points['weighted'].to_file(driver = 'ESRI Shapefile', filename= out_dir + "weighted.shp")
# fp_path.path_points['equal'].to_file(driver = 'ESRI Shapefile', filename= out_dir + "equal.shp")
