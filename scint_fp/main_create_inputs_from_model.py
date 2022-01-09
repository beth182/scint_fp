import pandas as pd
import numpy as np
import copy

import tkinter
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
matplotlib.use('TkAgg')

from scint_flux.functions import iterative_stability
from scint_flux.functions import wx_data
from scint_flux import constants

from scint_fp.functions import wx_u_v_components
from scint_fp.functions import model_inputs
from scint_fp.functions import time_average_sa_input

DOYstart_choice = 2016142  # CHANGE HERE
DOYstop_choice = 2016142

out_dir = 'test_outputs/'

# get roughness length from the grid directly overlaying the centre of the path
# ToDo: for now, this is hard coded because I am only looking at one path. In the future this should be flexable

# grid 13 is over the centre of path BCT -> IMU
path_number = 13
# this is model grid IMU E with roughness val of 0.7724066
model_site = 'IMU'
model_grid_letter = 'E'
z0_centre_grid = 0.7724066

# going for model level at a height of 58.8 m above model ground
target_model_level = 70

# get the wind speed of the model
mod_wind_time, mod_wind_vals, mod_wind_height = model_inputs.collect_model_inputs(DOYstart_choice, DOYstop_choice, '21Z', 'wind',
                                                                        target_model_level, model_site,
                                                                        model_grid_letter, path_number)
mod_ws = mod_wind_vals['ws']
mod_wd = mod_wind_vals['wd']

# construct array of length mod_wind_time full of tair heights
mod_wind_height_array = np.ones(len(mod_wind_time))*mod_wind_height


# get model Tair
mod_tair_time, mod_tair_vals, mod_tair_height = model_inputs.collect_model_inputs(DOYstart_choice, DOYstop_choice, '21Z', 'Tair',
                                                                        target_model_level, model_site,
                                                                        model_grid_letter, path_number)
# construct array of length mod_tair_time full of tair heights
mod_tair_height_array = np.ones(len(mod_tair_time))*mod_tair_height


# get model pressure
mod_press_time, mod_press_vals, mod_press_height = model_inputs.collect_model_inputs(DOYstart_choice, DOYstop_choice, '21Z', 'Press',
                                                                        target_model_level, model_site,
                                                                        model_grid_letter, path_number)
# construct array of length mod_press_time full of tair heights
mod_press_height_array = np.ones(len(mod_press_time))*mod_press_height

# get model BL flux (QH)
mod_BLflux_time, mod_BLflux_vals, mod_BLflux_height = model_inputs.collect_model_inputs(DOYstart_choice, DOYstop_choice, '21Z', 'BL_H',
                                                                        target_model_level, model_site,
                                                                        model_grid_letter, path_number)
# construct array of length mod_BLflux_time full of tair heights
mod_BLflux_height_array = np.ones(len(mod_BLflux_time))*mod_BLflux_height


assert mod_wind_time.all() == mod_tair_time.all() == mod_press_time.all() == mod_BLflux_time.all()

# construct array of length mod_time full of model z0 heights
mod_z0_array = np.ones(len(mod_BLflux_time))*z0_centre_grid

# construct df of all the extracted model values
df_dict = {'time': mod_wind_time,
           'wind_speed_convert': mod_ws, 'wind_direction_convert': mod_wd, 'z_wind': mod_wind_height_array,
           't_air': mod_tair_vals, 'z_t_air': mod_tair_height_array,
           'press_adj': mod_press_vals, 'z_press': mod_press_height_array,
           'QH': mod_BLflux_vals, 'z_BL_flux': mod_BLflux_height_array,
           'z0_model': mod_z0_array}
df = pd.DataFrame(df_dict)
df = df.set_index('time')

# calculate density and add to df
df = wx_data.density_calc(df)


# calculate initial estimate of ustar
initial_ustar = iterative_stability.calculate_initial_ustar(ws=mod_ws,
                                                            z_effective=mod_wind_height,
                                                            z0=z0_centre_grid)
# calculate initial estimate of L
initial_L = iterative_stability.calculate_initial_L_no_model_term(initial_ustar, df)



neutral_limit = 0.03
ustar_threshold=0.05
iteration_limit=50

# create empty
ustar_list = []
tstar_list = []
L_list = []
fmo_list = []
stab_param_list = []

iteration_count_list = []
iteration_dict_L = {}
iteration_dict_ustar = {}

# for each time
for a in range(0, len(df.index)):

    # get hour as string for key to dict
    time_key = df.index[a]

    # setting a condition to break loop as initially False
    # will keep looping until the difference in ustar output is smaller than ustar_threshold
    threshold_reached = False

    # define initial stability
    L_initial = initial_L[a]
    ustar_initial = initial_ustar[a]

    # counter to log how many iterations we've gone through
    iteration_count = 0

    # define list where all values from iterations are stored
    iteration_L_vals = []
    iteration_ustar_vals = []

    # while the condition has not be satisfied
    while not threshold_reached:

        # for the first iteration, take L initial as L
        if iteration_count == 0:
            L_previous = copy.copy(L_initial)
            ustar_previous = copy.copy(ustar_initial)

            # append initial values to iteration list
            iteration_L_vals.append(L_initial)
            iteration_ustar_vals.append(ustar_initial)

        # if not the first iteration, take a copy of the previous values
        else:
            L_previous = copy.copy(L)
            ustar_previous = copy.copy(ustar)

        if L_previous == 0.0:
            L_previous = 0.0000000000001
        elif L_previous == -0.0:
            L_previous = -0.0000000000001

        # calculate stability param z/L
        stab_param = df['z_wind'][a] / L_previous

        if stab_param < -neutral_limit:  # if unstable

            #  stability-adjusted logarithmic profile to estimate ustar
            # see equation 3 & 4 in Grimmond and Cleugh 1994
            # coefficants updated as per Foken Micromet textbook, page 61

            Phi = iterative_stability.phi_unstable(stab_param)
            Phi0 = iterative_stability.phi_unstable(df['z0_model'][a] / L_previous)


        elif stab_param > neutral_limit:  # stable

            #  stability-adjusted logarithmic profile to estimate ustar
            # from Grimmond and Cleugh 1994, equation 6

            Phi = iterative_stability.phi_stable(stab_param)
            Phi0 = iterative_stability.phi_stable(df['z0_model'][a] / L_previous)


        elif -neutral_limit <= stab_param <= neutral_limit:  # neutral

            Phi = 0
            Phi0 = 0

        if np.isnan(L_initial):
            threshold_reached = True
            ustar = np.nan
            tstar = np.nan
            L = np.nan
            fmo = np.nan
            stab_param = np.nan

        else:
            # ustar
            ustar = iterative_stability.ustar_eq(df['wind_speed_convert'][a], df['z_wind'][a], df['z0_model'][a], Phi, Phi0)

            # calculate L
            L = iterative_stability.obukhov_length_with_qh(ustar, np.asarray(df['density'])[a], np.asarray(df['t_air'])[a], np.asarray(df['QH'])[a])

        # check to see if condition is met if we aren't on the first iteration
        if iteration_count != 0:
            if np.abs(ustar - ustar_previous) <= ustar_threshold:
                threshold_reached = True
            else:
                print(np.abs(ustar - ustar_previous))

        if iteration_count > iteration_limit:
            threshold_reached = True
            ustar = np.nan
            L = np.nan
            stab_param = np.nan

        iteration_count += 1
        iteration_ustar_vals.append(ustar)
        iteration_L_vals.append(L)

    # append each hour's values to lists
    ustar_list.append(ustar)
    L_list.append(L)
    stab_param_list.append(stab_param)

    iteration_count_list.append(iteration_count)

    # just in case this is needed in future
    iteration_dict_L[time_key] = iteration_L_vals
    iteration_dict_ustar[time_key] = iteration_ustar_vals

iter_dict = {'time': df.index, 'ustar': ustar_list, 'L': L_list,
             'iter_count': iteration_count_list,
             'stab_param': stab_param_list}

# construct pandas df
iter = pd.DataFrame(iter_dict, columns=iter_dict.keys())
iter = iter.set_index('time')

df = pd.concat([df, iter], axis=1)



# looking at observation sig v

obs_inputs = out_dir + 'met_inputs_hourly_' + str(DOYstart_choice)[-3:] + '.csv'
obs_df = pd.read_csv(obs_inputs)
obs_df['Unnamed: 0'] = pd.to_datetime(obs_df['Unnamed: 0'], format='%Y%m%d %H:%M:%S')
obs_df.rename(columns={'Unnamed: 0':'time'}, inplace=True)
obs_df.rename(columns={'sig_v':'obs_sig_v'}, inplace=True)
obs_df.rename(columns={'wind_direction':'wind_direction_obs'}, inplace=True)
obs_df = obs_df.set_index('time')
obs_sigv = obs_df.obs_sig_v
obs_wd = obs_df.wind_direction_obs
df = pd.concat([df, obs_sigv], axis=1)
df = pd.concat([df, obs_wd], axis=1)


# looking at the variability of the v component or direction for the 3hours
# IE +/- 1 on the hour of interest
component_df = wx_u_v_components.ws_wd_to_u_v(df['wind_speed_convert'], df['wind_direction_convert'])
df = pd.concat([df, component_df], axis=1)

df['time'] = df.index
df.index = np.arange(0, len(df))


sig_v_list = []

dv1_list = []
dv2_list = []
dv3_list = []


for index, row in df.iterrows():

    if index == 0 or index == 23:
        sig_v_list.append(np.nan)

        dv1_list.append(np.nan)
        dv2_list.append(np.nan)
        dv3_list.append(np.nan)


    else:
        v_component = row['v_component']

        prev_v = df.loc[index-1, 'v_component']
        next_v = df.loc[index+1, 'v_component']

        array_of_vals = np.array([prev_v, v_component, next_v])

        sig_v = np.std(array_of_vals, axis=0)
        sig_v_list.append(sig_v)


        dv1 = np.abs(prev_v - v_component)
        dv2 = np.abs(v_component - next_v)
        dv3 = np.abs(prev_v - next_v)

        dv1_list.append(dv1)
        dv2_list.append(dv2)
        dv3_list.append(dv3)


df['sig_v'] = sig_v_list

df['dv1'] = dv1_list
df['dv2'] = dv2_list
df['dv3'] = dv3_list

df = df.set_index('time')

# plt.figure(figsize=(7,7))
# plt.scatter(df.obs_sig_v, df.dv1, label='T-1 -> T', color='orange', marker='o')
# plt.scatter(df.obs_sig_v, df.dv2, label='T -> T+1', color='green', marker='o')
# plt.scatter(df.obs_sig_v, df.dv3, label='T-1 -> T+1', color='blue', marker='o')
# plt.xlabel('Obs $\sigma$v (m s$^{-1}$)')
# plt.ylabel('Modelled $\Delta$v (m s$^{-1}$)')
# plt.legend()
# plt.savefig('C:/Users/beths/Desktop/LANDING/deltav.png')

# fig = plt.figure(figsize=(7,7))
# ax = fig.add_subplot(111)
# plt.scatter(df.index, df.dv1/df.obs_sig_v, label='T-1 -> T', color='orange', marker='o')
# plt.ylabel('Modelled $\Delta$v / Obs $\sigma$v ')
# plt.xlabel('time')
# plt.gcf().autofmt_xdate(rotation=0)
# ax.xaxis.set_major_formatter(DateFormatter('%H'))
# plt.legend()
# plt.savefig('C:/Users/beths/Desktop/LANDING/deltav_time.png')

# fig = plt.figure(figsize=(7,7))
# ax = fig.add_subplot(111)
# plt.scatter(df.wind_direction_obs, df.dv1/df.obs_sig_v, label='T-1 -> T', color='orange', marker='o')
# plt.ylabel('Modelled $\Delta$v / Obs $\sigma$v ')
# plt.xlabel('obs wind direction')
# plt.legend()
# plt.savefig('C:/Users/beths/Desktop/LANDING/deltav_wd.png')

df = df.dropna()

df.to_csv(out_dir + 'met_inputs_ukv_' + str(DOYstart_choice)[-3:] + '.csv')

print('end')
