# Beth Saunders 20/12/2022
# A version of sa lines plot - for the combined raster plot

# imports
import pandas as pd
import rasterio.plot
import numpy as np
import geopandas as gpd
import matplotlib.colors as colors
import matplotlib as mpl
import matplotlib.lines as mlines
import os
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

import scint_fp.functions.plot_functions.plot_sa_lines.sa_lines_funs as sa_lines_funs

from scintools.PointFootprint import trim_fp

mpl.rcParams.update({'font.size': 15})


def reweight_fp(raster_array, path_id, target_percentage):
    """

    :param raster_array:
    :return:
    """

    # replace nans with 0s
    raster_array_copy = raster_array.copy()
    raster_array_copy[np.isnan(raster_array_copy)] = 0

    # dict of number of SAs present for each path
    path_total_dict = {'BCT_IMU': 1195.,
                       'SCT_SWT': 516.,
                       'BTT_BCT': 617.,
                       'IMU_BTT': 540.}
    raster_array_reweight = raster_array_copy / path_total_dict[path_id]

    trim = trim_fp(raster_array_reweight[0, :, :], target_percentage)['fp_trim']

    return trim


def plot_sa_lines_combined_raster(file_list,
                                  colour_dict,
                                  save_path,
                                  landcover_raster_filepath='C:/Users/beths/OneDrive - University of Reading/Model_Eval/QGIS/Elliott/LandUseMM_7classes_32631.tif'):
    """

    :return:
    """

    fig, ax = plt.subplots(figsize=(10, 10))

    # plot the land cover map
    landcover_raster = rasterio.open(landcover_raster_filepath)
    color_list_lc = ["white", "dimgrey", "lightgrey", "deepskyblue", "lawngreen", "darkgreen", "limegreen", "olive"]
    # make a color map of fixed colors
    cmap_lc = colors.ListedColormap(color_list_lc)
    bounds_lc = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    norm_lc = colors.BoundaryNorm(bounds_lc, cmap_lc.N)
    rasterio.plot.show(landcover_raster, ax=ax, cmap=cmap_lc, norm=norm_lc, interpolation='nearest', alpha=0.4)

    # plot the SAs
    for i, filename in enumerate(file_list):

        # labels as filename without .tif
        path_name = filename.split('.')[0].split('/')[-1]

        # determine colour
        if type(colour_dict[path_name]) == str:
            colour_here = colour_dict[path_name]
        else:
            colour_here = list(colour_dict[path_name])

        # plot path
        df_path = gpd.read_file(
            'D:/Documents/scint_plots/scint_plots/sa_position_and_lc_fraction/scint_path_shp/' + path_name + '.shp')
        df_path.plot(edgecolor=colour_here, ax=ax, linewidth=3.0, zorder=50)

        # deal with SA raster
        raster = rasterio.open(filename)

        raster_array_untrimmed = raster.read()

        fp_60 = reweight_fp(raster_array_untrimmed, path_name, 0.6)
        weight_dict = {'60': fp_60}

        linestyle_dict = {'60': 'dashdot'}

        for weight in weight_dict.keys():

            raster_array = weight_dict[weight]

            # make all 0 vals in array nan
            raster_array[raster_array == 0.0] = np.nan

            # force non-zero vals to be 1
            bool_arr = np.ones(raster_array.shape)

            # remove nans in bool array
            nan_index = np.where(np.isnan(raster_array))
            bool_arr[nan_index] = 0.0

            # get location of max val
            ind_max_2d = np.unravel_index(np.nanargmax(raster_array), raster_array.shape)[:]
            max_coords = raster.xy(ind_max_2d[0], ind_max_2d[1])

            # Plot the SA line
            line_label = path_name.split('_')[0] + ' ' + path_name.split('_')[1]

            rasterio.plot.show(bool_arr, transform=raster.transform, contour=True, contour_label_kws={}, ax=ax,
                               colors=[colour_here], linestyles=[linestyle_dict[weight]], zorder=40)

            if weight == '60':
                ax.scatter(max_coords[0], max_coords[1], color=colour_here, marker='o', s=60, label=line_label,
                           edgecolor='k', zorder=100)

    # plot coords of sites
    path_15_coords = 'C:/Users/beths/OneDrive - University of Reading/Scintillometers/QGIS/scint_locations/trusted_coords/pair_15.csv'
    path15_df = pd.read_csv(path_15_coords)
    path15_df = path15_df.set_index(path15_df.site)
    path_12_coords = 'C:/Users/beths/OneDrive - University of Reading/Scintillometers/QGIS/scint_locations/trusted_coords/pair_12.csv'
    path12_df = pd.read_csv(path_12_coords)
    path12_df = path12_df.set_index(path12_df.site)
    path_13_coords = 'C:/Users/beths/OneDrive - University of Reading/Scintillometers/QGIS/scint_locations/trusted_coords/pair_13.csv'
    path13_df = pd.read_csv(path_13_coords)
    path13_df = path13_df.set_index(path13_df.site)
    KSSW_coords_file = 'C:/Users/beths/OneDrive - University of Reading/Scintillometers/QGIS/scint_locations/trusted_coords/KSSW_coords.csv'
    KSSW_df = pd.read_csv(KSSW_coords_file)
    # BCT
    ax.scatter(path12_df.loc['BCT'].x, path12_df.loc['BCT'].y, edgecolor='k', color='yellow', marker='o', s=30,
               zorder=100)
    ax.annotate('BCT', (path12_df.loc['BCT'].x + 50, path12_df.loc['BCT'].y), fontsize=13)
    # IMU
    ax.scatter(path12_df.loc['IMU'].x, path12_df.loc['IMU'].y, edgecolor='k', color='yellow', marker='o', s=30,
               zorder=100)
    ax.annotate('IMU', (path12_df.loc['IMU'].x + 50, path12_df.loc['IMU'].y), fontsize=13)
    # BTT
    ax.scatter(path13_df.loc['BTT'].x, path13_df.loc['BTT'].y, edgecolor='k', color='yellow', marker='o', s=30,
               zorder=100)
    ax.annotate('BTT', (path13_df.loc['BTT'].x - 500, path13_df.loc['BTT'].y), fontsize=13)
    # SWT
    ax.scatter(path15_df.loc['SWT'].x, path15_df.loc['SWT'].y, edgecolor='k', color='yellow', marker='o', s=30,
               zorder=100)
    ax.annotate('SWT', (path15_df.loc['SWT'].x + 50, path15_df.loc['SWT'].y), fontsize=13)
    # SCT
    ax.scatter(path15_df.loc['SCT'].x, path15_df.loc['SCT'].y, edgecolor='k', color='yellow', marker='o', s=30,
               zorder=100)
    ax.annotate('SCT', (path15_df.loc['SCT'].x - 500, path15_df.loc['SCT'].y), fontsize=13)
    # KSSW
    ax.scatter(KSSW_df.X_32631[0], KSSW_df.Y_32631[0], edgecolor='k', color='yellow', marker='o', s=30, zorder=100)
    ax.annotate('KSSW', (KSSW_df.X_32631[0] + 50, KSSW_df.Y_32631[0] + 50), fontsize=13)

    # plot UKV grids at centre of paths
    # read in the UKV grid geo-reference data for each grid
    ukv_shp_13 = 'C:/Users/beths/OneDrive - University of Reading/UKV_grid_objects/grid_line_shp_files/13.shp'
    ukv_shp_12 = 'C:/Users/beths/OneDrive - University of Reading/UKV_grid_objects/grid_line_shp_files/12.shp'
    ukv_shp_37 = 'C:/Users/beths/OneDrive - University of Reading/UKV_grid_objects/grid_line_shp_files/37.shp'
    ukv_shp_13_df = gpd.read_file(ukv_shp_13)
    ukv_shp_13_df.plot(edgecolor='grey', ax=ax, zorder=30)
    ukv_shp_12_df = gpd.read_file(ukv_shp_12)
    ukv_shp_12_df.plot(edgecolor='grey', ax=ax, zorder=30)
    ukv_shp_37_df = gpd.read_file(ukv_shp_37)
    ukv_shp_37_df.plot(edgecolor='grey', ax=ax, zorder=30, label='UKV')

    handles, labels = ax.get_legend_handles_labels()

    line_60 = mlines.Line2D([], [], color='k', linestyle=linestyle_dict['60'], label='60%')

    handles.append(line_60)

    plt.legend(handles=handles, loc='upper left')
    plt.yticks(rotation=90)

    # limits which stay constant between and which suit the SAs
    ax.set_xlim(277277.92426043435, 288387.33066867734)
    ax.set_ylim(5706625.265920927, 5717734.67232917)

    plt.savefig(save_path + 'sa_lines_combine.png', bbox_inches='tight', dpi=300)
    # plt.show()

    print('end')


def plot_sa_lines_combined_raster_panels(file_list,
                                         colour_dict,
                                         save_path,
                                         landcover_raster_filepath='C:/Users/beths/OneDrive - University of Reading/Model_Eval/QGIS/Elliott/LandUseMM_7classes_32631.tif'):
    """

    :return:
    """

    fig = plt.figure(figsize=(10, 10))

    ax1 = plt.subplot(2, 2, 1)
    ax2 = plt.subplot(2, 2, 2)
    ax3 = plt.subplot(2, 2, 3)
    ax4 = plt.subplot(2, 2, 4)

    axs = [ax1, ax2, ax3, ax4]

    # plot the land cover map
    landcover_raster = rasterio.open(landcover_raster_filepath)
    color_list_lc = ["white", "dimgrey", "lightgrey", "deepskyblue", "lawngreen", "darkgreen", "limegreen", "olive"]
    # make a color map of fixed colors
    cmap_lc = colors.ListedColormap(color_list_lc)
    bounds_lc = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    norm_lc = colors.BoundaryNorm(bounds_lc, cmap_lc.N)

    for axis in axs:
        rasterio.plot.show(landcover_raster, ax=axis, cmap=cmap_lc, norm=norm_lc, interpolation='nearest', alpha=0.4)

        # limits which stay constant between and which suit the SAs
        axis.set_xlim(277277.92426043435, 288387.33066867734)
        axis.set_ylim(5706625.265920927, 5717734.67232917)

        # remove x and y ticks
        axis.set_xticks([])
        axis.set_yticks([])
        axis.set_aspect('equal')

    # plot the SAs
    for i, filename in enumerate(file_list):

        if 'SCT_SWT' in filename:
            axis = ax4
        elif 'BCT_IMU' in filename:
            axis = ax2
        elif 'BTT_BCT' in filename:
            axis = ax3
        else:
            assert 'IMU_BTT' in filename
            axis = ax1

        # labels as filename without .tif
        path_name = filename.split('.')[0].split('/')[-1]

        # determine colour
        if type(colour_dict[path_name]) == str:
            colour_here = colour_dict[path_name]
        else:
            colour_here = list(colour_dict[path_name])

        # deal with SA raster
        raster = rasterio.open(filename)

        raster_array_untrimmed = raster.read()

        fp_40 = reweight_fp(raster_array_untrimmed, path_name, 0.4)
        fp_50 = reweight_fp(raster_array_untrimmed, path_name, 0.5)
        fp_60 = reweight_fp(raster_array_untrimmed, path_name, 0.6)
        weight_dict = {'40': fp_40, '50': fp_50, '60': fp_60}

        linestyle_dict = {'60': 'dashdot', '50': (0, (5, 6)), '40': 'dotted'}

        for weight in weight_dict.keys():

            raster_array = weight_dict[weight]

            # make all 0 vals in array nan
            raster_array[raster_array == 0.0] = np.nan

            # force non-zero vals to be 1
            bool_arr = np.ones(raster_array.shape)

            # remove nans in bool array
            nan_index = np.where(np.isnan(raster_array))
            bool_arr[nan_index] = 0.0

            # get location of max val
            ind_max_2d = np.unravel_index(np.nanargmax(raster_array), raster_array.shape)[:]
            max_coords = raster.xy(ind_max_2d[0], ind_max_2d[1])

            # Plot the SA line
            sas = rasterio.plot.show(bool_arr, transform=raster.transform, contour=True, contour_label_kws={}, ax=axis,
                                     colors=[colour_here], linestyles=[linestyle_dict[weight]])

            plt.setp(sas.collections, linewidth=1)

            if weight == '60':
                axis.scatter(max_coords[0], max_coords[1], color=colour_here, marker='o', s=30)

                # plot a solid colour in the 60 extent
                shade_array = bool_arr.copy()
                shade_array[shade_array == 0] = np.nan

                # faff with custom cmap for just 1 colour
                vmax = 3.0
                cmap_path = LinearSegmentedColormap.from_list('mycmap', [(0 / vmax, 'white'),
                                                                         (1 / vmax, colour_here),
                                                                         (3 / vmax, 'white')])
                rasterio.plot.show(shade_array, transform=raster.transform, ax=axis, cmap=cmap_path, vmin=0, vmax=vmax,
                                   alpha=0.1)

        # plot path
        df_path = gpd.read_file(
            'D:/Documents/scint_plots/scint_plots/sa_position_and_lc_fraction/scint_path_shp/' + path_name + '.shp')
        df_path.plot(edgecolor=colour_here, ax=axis, linewidth=2.0)

    handles, labels = ax1.get_legend_handles_labels()

    line_60 = mlines.Line2D([], [], color='k', linestyle=linestyle_dict['60'], label='60%')
    line_50 = mlines.Line2D([], [], color='k', linestyle=linestyle_dict['50'], label='50%')
    line_40 = mlines.Line2D([], [], color='k', linestyle=linestyle_dict['40'], label='40%')

    handles.append(line_60)
    handles.append(line_50)
    handles.append(line_40)

    plt.legend(handles=handles, loc='upper left')

    plt.tight_layout()
    fig.subplots_adjust(hspace=0.01, wspace=0.01)

    plt.savefig(save_path + 'sa_lines_combine_panels.png', bbox_inches='tight', dpi=300)
    # plt.show()

    print('end')


if __name__ == '__main__':
    sa_file_source_list = ['IMU_BTT.tif', 'BCT_IMU.tif', 'BTT_BCT.tif', 'SCT_SWT.tif']

    colour_dict = {'BCT_IMU': 'red', 'SCT_SWT': 'mediumorchid', 'IMU_BTT': 'green', 'BTT_BCT': 'blue'}

    file_list = sa_lines_funs.find_SA_rasters(given_list=True,
                                              sa_main_dir='C:/Users/beths/OneDrive - University of Reading/Paper 2/combine_rasters/',
                                              sa_file_source=sa_file_source_list)

    save_path = os.getcwd().replace('\\', '/') + '/'

    plot_sa_lines_combined_raster(file_list=file_list, colour_dict=colour_dict, save_path=save_path)
    # plot_sa_lines_combined_raster_panels(file_list=file_list, colour_dict=colour_dict, save_path=save_path)

    print('end')
