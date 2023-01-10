# Beth Saunders 10/01/2023
# script to plot wind roses - to represent the climatology of the the combine SA plots

# imports
import matplotlib.cm as cm
import numpy as np
from windrose import WindroseAxes
import matplotlib as mpl
import pandas as pd
import os
import matplotlib.pyplot as plt

mpl.rcParams.update({'font.size': 15})

from scint_flux.functions import read_calculated_fluxes

save_path = os.getcwd().replace('\\', '/') + '/'
path_name = 'SCT_SWT'

if path_name == 'BCT_IMU':
    path_col = 'P12'
elif path_name == 'SCT_SWT':
    path_col = 'P15'
elif path_name == 'BTT_BCT':
    path_col = 'P11'
else:
    assert path_name == 'IMU_BTT'
    path_col = 'P13'

# find wind data

days_df_path = 'C:/Users/beths/OneDrive - University of Reading/Paper 2/all_days.csv'
days_df = pd.read_csv(days_df_path)
df_selected = days_df.iloc[np.where(days_df[path_col] == 1)[0]][['year', 'DOY', path_col]]
DOY_list = list((df_selected.year.astype(str) + df_selected.DOY.astype(str)).astype(int))

df = read_calculated_fluxes.extract_data(doy_list=DOY_list,
                                         pair_id=path_name,
                                         var_list=['wind_speed_adj', 'wind_direction_corrected'],
                                         time_res='1min_sa10_mins_ending')

# format df as I want it
df = df.drop('z_f', axis=1)
df = df.dropna()
df = df.rename(columns={'wind_speed_adj': 'speed', 'wind_direction_corrected': 'direction'})


def plot_windrose(df,
                  path_name,
                  save_path):
    colour_dict = {'BCT_IMU': 'red', 'SCT_SWT': 'mediumorchid', 'IMU_BTT': 'green', 'BTT_BCT': 'blue'}

    color_here = colour_dict[path_name]

    mpl.rc('axes', edgecolor=color_here, linewidth=5)

    bins_range = np.arange(1, 12, 2)
    ax = WindroseAxes.from_ax()

    # bar
    """
    ax.bar(df.direction, df.speed, normed=True, bins=bins_range)
    ax.legend(loc='center left', bbox_to_anchor=(-0.2, 0.1))
    """

    # contour
    # """
    ax.contourf(df.direction, df.speed, normed=True, bins=bins_range, cmap=cm.plasma_r)
    ax.contour(df.direction, df.speed, normed=True, bins=bins_range, colors='black', linewidth=0.5)
    # """

    ax.legend(loc='center left', bbox_to_anchor=(-0.3, 0.1))
    ax.set_yticks(np.arange(10, 40, step=10))
    ax.set_yticklabels(np.arange(10, 40, step=10))

    plt.savefig(save_path + 'windrose_' + path_name + '.png', bbox_inches='tight', dpi=300)
    print('end')


plot_windrose(df, path_name)

print('end')
