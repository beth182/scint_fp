# Beth Saunders 09/09/2021

# imports
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt

from scint_flux import run_function
from scint_flux.functions import plots
from scint_flux.functions import benchmark

from scint_fp.functions import wx_u_v_components
from scint_fp.functions import time_average_sa_input
from scint_fp.functions import sa_creation_selecting
from scint_fp.functions import retrieve_var

# USER CHOICE

# ToDo: be able to do more than one day
DOY_start = 2016267
DOY_stop = 2016267

average_period = 10
# average_period = 60

mins_ending_10 = True
unstable_only = True

pair_id = 'BCT_IMU'

# define site where the radiation data comes from
rad_site = 'KSSW'

# out_dir = 'C:/Users/beths/Desktop/LANDING/fp_output/'
out_dir = 'test_outputs/wd_corrected/'
# out_dir = 'test_outputs/'

bdsm_path = 'D:/Documents/scintools/example_inputs/rasters/height_surface_4m.tif'
cdsm_path = 'D:/Documents/scintools/example_inputs/rasters/height_veg_4m.tif'
dem_path = 'D:/Documents/scintools/example_inputs/rasters/height_terrain_4m.tif'

raw_scint_path = '//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_raw/'
processed_wx_path = '//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_scint/'
# raw_scint_path = 'C:/Users/beths/Desktop/LANDING/data_wifi_problems/'
# processed_wx_path = 'C:/Users/beths/Desktop/LANDING/data_wifi_problems/'

# bdsm_path = '/storage/basic/micromet/Tier_processing/rv006011/PycharmProjects/scintools/example_inputs/rasters/height_surface_4m.tif'
# cdsm_path = '/storage/basic/micromet/Tier_processing/rv006011/PycharmProjects/scintools/example_inputs/rasters/height_veg_4m.tif'
# dem_path = '/storage/basic/micromet/Tier_processing/rv006011/PycharmProjects/scintools/example_inputs/rasters/height_terrain_4m.tif'
# raw_scint_path = '/storage/basic/micromet/Tier_raw/'
# processed_wx_path = '/storage/basic/micromet/Tier_processing/rv006011/new_data_scint/'

########################################################################################################################

start_dt = dt.datetime.strptime(str(DOY_start), '%Y%j')
stop_dt = dt.datetime.strptime(str(DOY_stop), '%Y%j')

delta = stop_dt - start_dt

doy_list = []
for i in range(delta.days + 1):
    day = start_dt + dt.timedelta(days=i)
    doy_list.append(day.strftime('%Y%j'))

df_list = []

for doy in doy_list:

    df = run_function.main_QH_calcs(doy=doy,
                                    pair_id=pair_id,
                                    sa_res=average_period,
                                    raw_scint_path=raw_scint_path,
                                    processed_wx_path=processed_wx_path,
                                    bdsm_path=bdsm_path,
                                    cdsm_path=cdsm_path,
                                    dem_path=dem_path,
                                    las_instrument_type='LASMkII_29',
                                    sa_path=False,
                                    write_file=False)

    # plots.plot_qh(df)

    # APPEND BEFORE AVERAGING
    df_list.append(df)

    # wind calculations
    component_df = wx_u_v_components.ws_wd_to_u_v(df['wind_speed_adj'], df['wind_direction_corrected'])
    df = pd.concat([df, component_df], axis=1)

    # take the last 10 minute averages and calculate the standard deviation of wind for that period
    df_av = time_average_sa_input.time_average_sa(df, average_period)

    # convert the averages of the u and the v component back to wind speed and direction
    av_comp = wx_u_v_components.u_v_to_ws_wd(df_av['u_component'], df_av['v_component'])
    df_av = pd.concat([df_av, av_comp], axis=1)

    # determine which times are made into source areas here:
    ########################################################################################################################
    df_selection = df_av

    # find unstable times only

    if unstable_only:
        df_selection = sa_creation_selecting.find_unstable_times(df_selection, neutral_limit=0.03)

    # remove nan rows
    df_selection = sa_creation_selecting.remove_nan_rows(df_selection)

    if average_period == 10:
        if mins_ending_10:
            # only take the 10-min average SAs on the hour ending
            df_selection = retrieve_var.take_hourly_vars(df_selection)

    ########################################################################################################################
    # save to csv
    if average_period == 10:
        if unstable_only:
            if mins_ending_10:
                csv_out_string = 'met_inputs_minutes_ending_'
            else:
                csv_out_string = 'met_inputs_minutes_'
        else:
            if mins_ending_10:
                csv_out_string = 'met_inputs_minutes_all_stab_ending_'
            else:
                csv_out_string = 'met_inputs_minutes_all_stab_'
    elif average_period == 60:
        if unstable_only:
            csv_out_string = 'met_inputs_hourly_'
        else:
            csv_out_string = 'met_inputs_hourly_all_stab_'

    df_selection.to_csv(out_dir + csv_out_string + str(doy)[-3:] + '.csv')

# df_all = pd.concat(df_list)
# plots.plot_qh(df_all)
# pair = run_function.construct_path(pair_id, bdsm_path, cdsm_path, dem_path)['pair']
# benchmark.test_l1_qh(df_all, DOY_start, DOY_stop, pair)

print('END')
