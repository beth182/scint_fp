# check the met conditions of an example day/ period

# imports
import pandas as pd
import matplotlib.pyplot as plt
from scint_fp.functions import wx_u_v_components
import numpy as np

from scint_flux import look_up
from scint_flux.functions import find_files
import scintools as sct
from scint_flux.functions import wx_data
from scint_fp.functions import time_average_sa_input

doy_start = 2016118  # CHANGE HERE
doy_end = 2016118

pair = sct.ScintillometerPair(x=[look_up.BCT_info['x'], look_up.IMU_info['x']],
                              y=[look_up.BCT_info['y'], look_up.IMU_info['y']],
                              z_asl=[look_up.BCT_info['z_asl'], look_up.IMU_info['z_asl']],
                              pair_id='BCT_IMU',
                              crs='epsg:32631')

main_dir_tier_raw = '//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_raw/'
main_dir_new_data_scint = '//rdg-home.ad.rdg.ac.uk/research-nfs/basic/micromet/Tier_processing/rv006011/new_data_scint/'

wx_files = find_files.find_files(doy_start=doy_start, doy_end=doy_end, site=pair.pair_id.split('_')[0],
                                 instrument='Davis', level='L2', time_res='1min',
                                 main_dir=main_dir_new_data_scint)

# create new columns
df = pd.DataFrame({'wind_speed': [], 't_air': [], 'r_h': [], 'pressure': [], 'rain_rate': [], 'z_wx': []})

for i in range(0, len(wx_files['file_paths'])):
    # process wx
    process_df = wx_data.create_wx_df(file_path=wx_files['file_paths'][i])

    # append to existing dataframe
    df = df.append(process_df)

component_df = wx_u_v_components.ws_wd_to_u_v(df['wind_speed'], df['wind_direction'])

df = pd.concat([df, component_df], axis=1)

df_av = time_average_sa_input.time_average_sa(df, 10)

test = wx_u_v_components.u_v_to_ws_wd(df['u_component'], df['v_component'])

av_comp = wx_u_v_components.u_v_to_ws_wd(df_av['u_component'], df_av['v_component'])

df_av = pd.concat([df_av, av_comp], axis=1)

print('end')
