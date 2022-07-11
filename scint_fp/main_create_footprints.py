
import pandas as pd
import scintools as sct
import numpy as np

from scint_flux import look_up

csv_name = 'met_inputs_hourly_176.csv'  # CHANGE HERE
print(csv_name)

# CHANGE HERE
# LOCAL
out_dir = 'test_outputs/wd_corrected/'
bdsm_path = 'D:/Documents/scintools/example_inputs/rasters/height_surface_4m.tif'
cdsm_path = 'D:/Documents/scintools/example_inputs/rasters/height_veg_4m.tif'
dem_path = 'D:/Documents/scintools/example_inputs/rasters/height_terrain_4m.tif'

# CHANGE HERE
# CLUSTER
# out_dir = '/storage/basic/micromet/Tier_processing/rv006011/PycharmProjects/scintillometer_footprints/scint_fp/test_outputs/'
# bdsm_path = '/storage/basic/micromet/Tier_processing/rv006011/PycharmProjects/scintools/example_inputs/rasters/height_surface_4m.tif'
# cdsm_path = '/storage/basic/micromet/Tier_processing/rv006011/PycharmProjects/scintools/example_inputs/rasters/height_veg_4m.tif'
# dem_path = '/storage/basic/micromet/Tier_processing/rv006011/PycharmProjects/scintools/example_inputs/rasters/height_terrain_4m.tif'

pair_id = 'BCT_IMU'
# construct path using scintools
tr_string = pair_id.split('_')[0]
rx_string = pair_id.split('_')[1]

pair = sct.ScintillometerPair(x=[look_up.site_info[tr_string]['x'], look_up.site_info[rx_string]['x']],
                              y=[look_up.site_info[tr_string]['y'], look_up.site_info[rx_string]['y']],
                              z_asl=[look_up.site_info[tr_string]['z_asl'], look_up.site_info[rx_string]['z_asl']],
                              pair_id=pair_id,
                              crs='epsg:32631')

roughness_inputs = sct.RoughnessInputs()

spatial_inputs = sct.SpatialInputs(
    domain_size=15000,
    x=float(pair.path_center().x),
    y=float(pair.path_center().y),
    z_asl=pair.path_center_z(),
    bdsm_path=bdsm_path,
    cdsm_path=cdsm_path,
    dem_path=dem_path)

point_res = 50
weightings = (100, 200)
path_params = {'point_res': point_res,
               'weightings': weightings}


def create_footprints(pair, roughness_inputs, spatial_inputs, path_params,
                      out_dir, csv_name):

    # read inputs csv
    df = pd.read_csv(out_dir + csv_name)
    df.rename(columns={'Unnamed: 0': 'time'}, inplace=True)
    df.time = pd.to_datetime(df['time'], dayfirst=True)
    df = df.set_index('time')

    # df = df.between_time('11:00', '13:00')

    # create footprint for each entry in dataframe
    for index, row in df.iterrows():

        time = row.name
        sigv = row['sig_v']
        wd = row['wind_direction_convert']
        ustar = row['ustar']
        L = row['L']

        title_string = time.strftime('%Y') + '_' + time.strftime('%j') + '_' + time.strftime('%H_%M')

        print(' ')
        print(title_string)
        print(' ')

        met_inputs = sct.MetInputs(obukhov=L,
                                   sigv=sigv,
                                   ustar=ustar,
                                   wind_dir=wd
                                   )

        fp_path = sct.run_pathfootprint(scint_pair=pair,
                                        met_inputs=met_inputs,
                                        roughness_inputs=roughness_inputs,
                                        path_params=path_params,
                                        target_percentage=0.6,
                                        spatial_inputs=spatial_inputs)

        # ToDo: temp fix. Need to take out once fixed in scintools
        fp_path.roughness_outputs.z_m = -999.0
        fp_path.footprint[fp_path.footprint == 0.0] = np.nan

        string_to_save = str(pair.pair_id) + '_' + str(spatial_inputs.domain_size) + '_' + title_string
        file_out = out_dir + 'hourly/' + string_to_save + '.tif'
        fp_path.save(out_dir + 'hourly/' + string_to_save)
        fp_path.save_tiff(file_out)

        print(title_string)

        print('END')

    print('END')


create_footprints(pair, roughness_inputs, spatial_inputs, path_params,
                  out_dir, csv_name)

print('end')
