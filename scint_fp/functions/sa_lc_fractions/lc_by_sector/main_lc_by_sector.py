# Beth Saunders 13/01/23
# split landcover dataset into sectors by angle and calculate land cover fraction

# imports
import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from scint_fp.functions.sa_lc_fractions import lc_fractions_in_sa

save_path = os.getcwd().replace('\\', '/') + '/'

# run this to make sector rasters
"""
from scint_fp.functions.sa_lc_fractions.lc_by_sector import mask_SA_by_sector
from shapely.geometry import Point

import scintools as sct

# define a centre point (in this case, the centre of the path)
# path 12 - BCT -> IMU
pair_raw = sct.ScintillometerPair(x=[285440.6056, 284562.3107],
                                  y=[5712253.017, 5712935.032],
                                  z_asl=[142, 88],
                                  pair_id='BCT_IMU',
                                  crs='epsg:32631')

centre_point = Point(pair_raw.path_center()[0].x, pair_raw.path_center()[0].y)
raster_filepath = 'C:/Users/beths/OneDrive - University of Reading/Paper 2/combine_rasters/BCT_IMU.tif'

mask_SA_by_sector.mask_raster_by_sector(raster_filepath, centre_point, save_path)
"""

# landcover functions in each sector - weighted by SA


sa_sector_dir = save_path + 'sector_rasters/'

df = pd.DataFrame()

for file in os.listdir(sa_sector_dir):
    file_path = sa_sector_dir + file

    sa_df = lc_fractions_in_sa.landcover_fractions_in_SA_weighted(sa_tif_path=file_path,
                                                                  save_path=save_path)

    # getting df in correct format for bar plot
    df_sa_columns = ['Building', 'Impervious', 'Water', 'Grass', 'Deciduous', 'Evergreen', 'Shrub']
    df_sa_data = [[sa_df.loc[1]['sa_weight_percent'],
                   sa_df.loc[2]['sa_weight_percent'],
                   sa_df.loc[3]['sa_weight_percent'],
                   sa_df.loc[4]['sa_weight_percent'],
                   sa_df.loc[5]['sa_weight_percent'],
                   sa_df.loc[6]['sa_weight_percent'],
                   sa_df.loc[7]['sa_weight_percent']]]
    # a dataframe of one source area
    df_sa = pd.DataFrame(df_sa_data, columns=df_sa_columns)
    df_sa.index = [int(file.split('.')[0])]  # index as sector number

    df = df.append(df_sa)

df = df.sort_index()


def lc_polar_plot(path_name,
                  df):
    """

    :param path_name:
    :param df: landcover pandas dataframe
    :return:
    """

    # set the colours of the path
    colour_dict = {'BCT_IMU': 'red', 'SCT_SWT': 'mediumorchid', 'IMU_BTT': 'green', 'BTT_BCT': 'blue'}
    color_here = colour_dict[path_name]

    # deal with masked values in pandas df col
    for col_name in df.columns:
        df[col_name].iloc[~np.isin(np.arange(len(df)), np.where(df[col_name] >= 0)[0])] = 0

    # combine vegitation into one lc type
    df['Veg'] = df['Grass'] + df['Deciduous'] + df['Evergreen'] + df['Shrub']

    # define the angles of the sectors in the plot
    interval = 360 / len(df)
    start = interval / 2
    thetas = np.arange(start, 360, interval)
    assert len(thetas) == len(df)
    df['thetas'] = thetas

    # define width of sector
    width = [360 / len(df) for _ in range(len(df))]

    # set up plot
    fig = px.bar_polar(template="simple_white")

    # add each bar one by one

    fig.add_trace(go.Barpolar(
        r=list(df['Building']),
        theta=list(df['thetas']),
        marker_color='dimgrey',
        width=width,
        name='Building'))

    fig.add_trace(go.Barpolar(
        r=list(df['Impervious']),
        theta=list(df['thetas']),
        marker_color='lightgrey',
        width=width,
        name='Impervious'))

    fig.add_trace(go.Barpolar(
        r=list(df['Water']),
        theta=list(df['thetas']),
        marker_color='deepskyblue',
        width=width,
        name='Water'))

    fig.add_trace(go.Barpolar(
        r=list(df['Veg']),
        theta=list(df['thetas']),
        marker_color='lawngreen',
        width=width,
        name='Vegetation'))

    # fix layout
    layout_options = {"legend_x": 0.15,
                      "legend_y": 0.5,
                      # "polar_radialaxis_ticks": "",
                      # "polar_radialaxis_showticklabels": False,
                      # "polar_angularaxis_ticks": "",
                      # "polar_angularaxis_showticklabels": False,
                      "font": {'size': 20},
                      "grid": {'ygap': 0}
                      }

    fig.update_layout(**layout_options)

    fig.update_traces(marker_line={'color': 'black'})
    fig.update_polars(radialaxis=dict(range=[0, 100],
                                      tickvals=[20, 40, 60, 80],
                                      # angle=90,
                                      # tickangle=90,
                                      linewidth=5,
                                      linecolor=color_here,
                                      color=color_here),
                      angularaxis=dict(linewidth=15,
                                       layer="below traces",
                                       linecolor=color_here,
                                       color=color_here,
                                       tickvals=[0, 45, 90, 135, 180, 225, 270, 315],
                                       ticktext=['N', 'N-E', 'E', 'S-E', 'S', 'S-W', 'W', 'N-W']
                                       ))

    # show figure and save manually
    fig.show()



lc_polar_plot('BCT_IMU', df)
print('end')
