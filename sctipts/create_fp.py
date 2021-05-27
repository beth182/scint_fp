import scintools as sct
import estimate_z0
import get_met_inputs
import qstar_stability_estimate

import numpy as np
import copy


out_dir = 'C:/Users/beths/Desktop/LANDING/fp_raster_tests/'


# files should be WX from new_scint_data, L2
# and scint data from new_scint_data, L1
wx_file_path_15min = '../example_data/Davis_BCT_2016142_15min_newdata_L2.nc'
wx_file_path_1min = '../example_data/Davis_BCT_2016142_1min_newdata_L2.nc'
scint_path = '../example_data/LASMkII_Fast_IMU_2016142_15min_newdata_L1.nc'

# random winter example
# wx_file_path_15min = './example_data/2016020/Davis_IMU_2016020_15min.nc'
# wx_file_path_1min = './example_data/2016020/Davis_IMU_2016020_1min.nc'
# scint_path = './example_data/2016020/LASMkII_Fast_IMU_2016020_15min.nc'

# wx_file_path_15min = './example_data/2016024/Davis_BCT_2016024_15min.nc'
# wx_file_path_1min = './example_data/2016024/Davis_BCT_2016024_1min.nc'
# scint_path = './example_data/2016024/LASMkII_Fast_IMU_2016024_15min.nc'

# define scint pair
# path 12 - BCT -> IMU
pair_raw = sct.ScintillometerPair(x=[285440.6056, 284562.3107],
                              y=[5712253.017, 5712935.032],
                              z_asl=[142, 88],
                              pair_id='BCT_IMU',
                              crs='epsg:32631')

pair = copy.deepcopy(pair_raw)

roughness_inputs = sct.RoughnessInputs()

point_res = 20
weightings = (50, 200)
path_params = {'point_res': point_res,
               'weightings': weightings}


spatial_inputs = sct.SpatialInputs(
    domain_size=15000,
    x=float(pair.path_center().x),
    y=float(pair.path_center().y),
    z_asl=pair.path_center_z(),
    bdsm_path='../../../example_inputs/rasters/height_surface_4m.tif',
    cdsm_path='../../../example_inputs/rasters/height_veg_4m.tif',
    dem_path='../../../example_inputs/rasters/height_terrain_4m.tif')


path_transect = pair.path_transect(dsm_file=spatial_inputs.bdsm_path, point_res=10)

# get effective beam height
zeff = path_transect.effective_beam_height()

# get estimate of z0 using estimate_z0
z0_scint = estimate_z0.calculate_quick_z0(spatial_inputs, crop_size=200)['z_0']


rad_file = '../example_data/CNR4_KSSW_2016142_15min.nc'
k = 0.4  # von-karman constant
g = 9.81  # acceleration due to gravity   (ms^-2)
cp = 1004.6  # specific heat capacity of dry air at constant P (J/kgK)
kelv = 273.15  # convert between celsius and kelvin
R = 2.87  # gas constant (for pressure in hPa)

QH_model = qstar_stability_estimate.simple_method_qh(rad_file)
initial_ustar = qstar_stability_estimate.calculate_initial_ustar(ws, zeff, z0_scint)




# need to seperate things out
# have a generic function for 'retreive this variable'
# or move everything over to new repo & utalise work already done on ob retrival in model eval
# to keep consistant

# need
# temperature
# pressure
# wind speed
# wind direction
# wind at higher time resolution
# Temperature structure parameter










met_inputs_fp = get_met_inputs.get_fp_met_inputs(wx_file_path_15min, wx_file_path_1min, scint_path, zeff, z0_scint)
hour_inputs = get_met_inputs.inputs_for_hour(met_inputs_fp)


def inputs_for_hour(hour_choice, hour_inputs):
    """

    Parameters
    ----------
    hour
    hour_inputs

    Returns
    -------

    """

    i = np.where([i.hour == hour_choice for i in hour_inputs['time']])

    time = hour_inputs['time'][i][0]
    sigv = hour_inputs['sigv'][i][0]
    wd = hour_inputs['wd'][i][0]
    L = hour_inputs['L'][i][0]
    ustar = hour_inputs['ustar'][i][0]

    hour_met_inputs = {'time': time, 'sigv': sigv, 'wd': wd, 'L': L, 'ustar': ustar}

    return hour_met_inputs


# hours_valid = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
# # for a selection of hours
# for hour in hours_valid:

# for all hours
for hour in range(0, 24):

    hour_met_inputs = inputs_for_hour(hour, hour_inputs)

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

    # fp_point = sct.run_footprint(met_inputs=met_inputs,
    #                              roughness_inputs=roughness_inputs,
    #                              spatial_inputs=spatial_inputs)
    #
    # fp_point.footprint[fp_point.footprint == 0.0] = np.nan

    fp_path = sct.run_footprintpath(scint_pair=pair,
                                    met_inputs=met_inputs,
                                    roughness_inputs=roughness_inputs,
                                    path_params=path_params,
                                    spatial_inputs=spatial_inputs)
    fp_path.footprint[fp_path.footprint == 0.0] = np.nan

    string_to_save = str(pair.pair_id) + '_' + str(spatial_inputs.domain_size) + '_' + title_string
    test_file_out = out_dir + string_to_save + '.tif'
    fp_path.save_tiff(test_file_out)

    print(title_string)

print('end')

# save path points
# fp_path.path_points['weighted'].to_file(driver = 'ESRI Shapefile', filename= out_dir + "weighted.shp")
# fp_path.path_points['equal'].to_file(driver = 'ESRI Shapefile', filename= out_dir + "equal.shp")