# Beth Saunders 09/09/2021

# imports
import scintools as sct
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scint_flux import look_up

from scint_flux.functions import find_files
from scint_flux.functions import read_raw
from scint_flux.functions import scint_methods
from scint_flux.functions import time_average
from scint_flux.functions import wx_data
from scint_flux.functions import rad_data
from scint_flux.functions import iterative_stability
from scint_flux.functions import adj_ws
from scint_flux.functions import quality_control
from scint_flux.functions import get_roughness_params
from scint_flux.functions import benchmark

from scint_fp.functions import estimate_roughness
from scint_fp.functions import wx_u_v_components
from scint_fp.functions import retrieve_var
from scint_fp.functions import inputs_at_given_hour
from scint_fp.functions import time_average_sa_input
from scint_fp.functions import sa_creation_selecting

# USER CHOICES
# doy_start = 2016111
# doy_end = 2016111

doy_start = 2016118  # CHANGE HERE
doy_end = 2016118

# define site where the radiation data comes from
rad_site = 'KSSW'

# out_dir = 'C:/Users/beths/Desktop/LANDING/fp_output/'
out_dir = 'test_outputs/'

# bdsm_path = 'D:/Documents/large_rasters/clipped/10_m_resampled/resample_10_surface.tif'
# cdsm_path = 'D:/Documents/large_rasters/clipped/10_m_resampled/resample_10_veg.tif'
# dem_path = 'D:/Documents/large_rasters/clipped/10_m_resampled/resample_10_terrain.tif'

bdsm_path = 'D:/Documents/scintools/example_inputs/rasters/height_surface_4m.tif'
cdsm_path = 'D:/Documents/scintools/example_inputs/rasters/height_veg_4m.tif'
dem_path = 'D:/Documents/scintools/example_inputs/rasters/height_terrain_4m.tif'

# bdsm_path = '/storage/basic/micromet/Tier_processing/rv006011/PycharmProjects/scintools/example_inputs/rasters/height_surface_4m.tif'
# cdsm_path = '/storage/basic/micromet/Tier_processing/rv006011/PycharmProjects/scintools/example_inputs/rasters/height_veg_4m.tif'
# dem_path = '/storage/basic/micromet/Tier_processing/rv006011/PycharmProjects/scintools/example_inputs/rasters/height_terrain_4m.tif'

# main_dir_tier_raw = '/storage/basic/micromet/Tier_raw/'
# main_dir_new_data_scint = '/storage/basic/micromet/Tier_processing/rv006011/new_data_scint/'

main_dir_tier_raw = '//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_raw/'
main_dir_new_data_scint = '//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_scint/'

# SCINT PROPERTIES #####################################################################################################
# construct path using scintools
pair = sct.ScintillometerPair(x=[look_up.BCT_info['x'], look_up.IMU_info['x']],
                              y=[look_up.BCT_info['y'], look_up.IMU_info['y']],
                              z_asl=[look_up.BCT_info['z_asl'], look_up.IMU_info['z_asl']],
                              pair_id='BCT_IMU',
                              crs='epsg:32631')

roughness_inputs = sct.RoughnessInputs()

point_res = 50
weightings = (100, 200)
path_params = {'point_res': point_res,
               'weightings': weightings}

spatial_inputs = sct.SpatialInputs(
    domain_size=15000,
    x=float(pair.path_center().x),
    y=float(pair.path_center().y),
    z_asl=pair.path_center_z(),
    bdsm_path=bdsm_path,
    cdsm_path=cdsm_path,
    dem_path=dem_path)

# SCINT DATA ###########################################################################################################
# find raw scintillometer files
raw_scint_files = find_files.find_files(doy_start=doy_start, doy_end=doy_end, site=pair.pair_id.split('_')[1],
                                        instrument='LASMkII_29', level='raw', time_res=None,
                                        main_dir=main_dir_tier_raw)

# create empty dataframe
scint_df = pd.DataFrame({'u_cn2': [], 'demod': [], 'sig_u_cn2': [], 'n_samples': []})

for i in range(0, len(raw_scint_files['file_paths'])):
    # construct dataframe of raw data
    raw_df = read_raw.read_raw_scint_file(file_path=raw_scint_files['file_paths'][i], date=raw_scint_files['dates'][i])

    # average data to required time resolution
    av_df = time_average.time_average_voltage(df=raw_df, minute_resolution=1)

    # append to existing dataframe
    scint_df = scint_df.append(av_df)

# calculate Cn2 using cn2 voltage output and update scint dataframe
scint_df = scint_methods.cn2_analogue_output(scint_df)

# benchmarking
# benchmark.test_l0_cn2(scint_df, doy_start, doy_end, pair)

# GET HEIGHTS ##########################################################################################################
# plot transect
path_transect = pair.path_transect(dsm_file=spatial_inputs.bdsm_path, point_res=10)

# get effective beam height
z_fb = path_transect.effective_beam_height()

# ROUGHNESS ESTIMATE ###################################################################################################
# get estimate of z0 using estimate_z0
roughness_estimate = estimate_roughness.calculate_quick_roughness(spatial_inputs, crop_size=200)

# add roughness columns to scint_df
z_d = np.ones(len(scint_df)) * roughness_estimate['z_d']
z_0 = np.ones(len(scint_df)) * roughness_estimate['z_0']
scint_df['z_d'] = z_d.tolist()
scint_df['z_0'] = z_0.tolist()

# calculate effective measurement height
df = get_roughness_params.calc_z_f(z_fb, scint_df)

# WX DATA ##############################################################################################################
# find wx files
wx_files = find_files.find_files(doy_start=doy_start, doy_end=doy_end, site=pair.pair_id.split('_')[0],
                                 instrument='Davis', level='L2', time_res='1min',
                                 main_dir=main_dir_new_data_scint)

# create new columns
wx_df = pd.DataFrame({'wind_speed': [], 't_air': [], 'r_h': [], 'pressure': [], 'rain_rate': [], 'z_wx': []})

for i in range(0, len(wx_files['file_paths'])):
    # process wx
    process_df = wx_data.create_wx_df(file_path=wx_files['file_paths'][i])

    # append to existing dataframe
    wx_df = wx_df.append(process_df)

df = wx_data.process_wx_data(df, wx_df)

# SCINT METHODS ########################################################################################################

# Quality control
df = quality_control.qc_functions(df=df, D=look_up.LAS_mk11_info['aperture_diameter'],
                                  wavelength=look_up.LAS_mk11_info['wavelength'],
                                  Lp=pair.path_length())

# calculate structure parameter coefficient and update dataframe
df = scint_methods.structure_parameter_coefficient(df)
# calculate the temperature structure parameter and update dataframe
df = scint_methods.temperature_structure_parameter(df)

# Benchmark
# benchmark.test_l1_ct2(df, doy_start, doy_end, pair)

# RADIATION FILES ######################################################################################################
# find radiation files
rad_files = find_files.find_files(doy_start=doy_start, doy_end=doy_end, site=rad_site,
                                  instrument='CNR4', level='L0', time_res='5s',
                                  main_dir=main_dir_tier_raw)

# create empty dataframe
rad_df = pd.DataFrame({'qstar': [], 'qstar_n_samples': []})

for i in range(0, len(rad_files['file_paths'])):
    # read radiation files
    rad_read_df = rad_data.process_rad_data(file_path=rad_files['file_paths'][i])

    # append to existing dataframe
    rad_df = rad_df.append(rad_read_df)

# add rad_df onto df
df = df.merge(rad_df, how='outer', left_index=True, right_index=True)

# STABILITY CALCS ######################################################################################################

# using simple method to model QH term using Q*
df = rad_data.simple_method_qh(df)

# adjust the wind speed at z met sensor to be at zf
df = adj_ws.adjust_ws_iteratively(df=df, ws=df['wind_speed'], ustar_threshold=0.05, iteration_limit=100, neutral_limit=0.03)

# calculate the fluxes
df = iterative_stability.andreas_flux_calc(df=df, ustar_threshold=0.05, neutral_limit=0.03)

# wind calculations
df = wx_u_v_components.wind_components(df)

# take the last 10 minute averages and calculate the standard deviation of wind for that period
df_av = time_average_sa_input.time_average_sa(df, 10)
# df_av = time_average_sa_input.time_average_sa(df, 60)  # CHANGE HERE

# determine which times are made into source areas here:
########################################################################################################################
# take 10-minute average values only ending on the hour
# df_selection = retrieve_var.take_hourly_vars(df_av)
df_selection = df_av

# find unstable times only
df_selection = sa_creation_selecting.find_unstable_times(df_selection, neutral_limit=0.03)

# remove nan rows
df_selection = sa_creation_selecting.remove_nan_rows(df_selection)

########################################################################################################################
# save to csv
df_selection.to_csv(out_dir + 'met_inputs_minutes_118.csv')  # CHANGE HERE

print('END')

