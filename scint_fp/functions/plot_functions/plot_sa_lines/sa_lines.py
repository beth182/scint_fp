import rasterio.plot
import numpy as np
import geopandas as gpd
import matplotlib.colors as colors
import matplotlib as mpl
import matplotlib.lines as mlines
import os
import matplotlib.pyplot as plt

from scintools.PointFootprint import trim_fp

import scint_fp.functions.plot_functions.plot_sa_lines.sa_lines_funs as sa_lines

mpl.rcParams.update({'font.size': 15})  # updating the matplotlib fontsize


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


def plot_sa_lines(file_list,
                  colour_list,
                  landcover_raster_filepath='C:/Users/beths/OneDrive - University of Reading/Model_Eval/QGIS/Elliott/LandUseMM_7classes_32631.tif',
                  given_list=True):
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
    rasterio.plot.show(landcover_raster, ax=ax, cmap=cmap_lc, norm=norm_lc, interpolation='nearest', alpha=0.5)

    # plot paths
    df_12 = gpd.read_file('D:/Documents/scint_plots/scint_plots/sa_position_and_lc_fraction/scint_path_shp/BCT_IMU.shp')
    df_12.plot(edgecolor='red', ax=ax, linewidth=3.0)

    df_11 = gpd.read_file('D:/Documents/scint_plots/scint_plots/sa_position_and_lc_fraction/scint_path_shp/BTT_BCT.shp')
    df_11.plot(edgecolor='blue', ax=ax, linewidth=3.0)

    df_15 = gpd.read_file('D:/Documents/scint_plots/scint_plots/sa_position_and_lc_fraction/scint_path_shp/SCT_SWT.shp')
    df_15.plot(edgecolor='green', ax=ax, linewidth=3.0)

    df_13 = gpd.read_file('D:/Documents/scint_plots/scint_plots/sa_position_and_lc_fraction/scint_path_shp/IMU_BTT.shp')
    df_13.plot(edgecolor='magenta', ax=ax, linewidth=3.0)

    left = []
    right = []
    top = []
    bottom = []

    # plot the SAs
    for i, filename in enumerate(file_list):

        if given_list:
            # labels as filename without .tif
            labels = filename.split('.')[0].split('/')[-1]

        else:
            # labels as time
            replc = filename.replace('.', '_')
            splt = replc.split('_')
            labels = splt[-3] + ':' + splt[-2]

        raster = rasterio.open(filename)

        left.append(raster.bounds.left)
        right.append(raster.bounds.right)
        top.append(raster.bounds.top)
        bottom.append(raster.bounds.bottom)

        raster_array_untrimmed = raster.read()

        fp_40 = reweight_fp(raster_array_untrimmed, labels, 0.4)
        fp_50 = reweight_fp(raster_array_untrimmed, labels, 0.5)
        fp_60 = reweight_fp(raster_array_untrimmed, labels, 0.6)
        weight_dict = {'40': fp_40, '50': fp_50, '60': fp_60}

        linestyle_dict = {'60': ':', '50': '-.', '40': '--'}

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

            if type(colour_list[i]) == str:
                colour_here = colour_list[i]
            else:
                colour_here = list(colour_list[i])

            line_label = labels.split('_')[0] + ' ' + labels.split('_')[1]

            rasterio.plot.show(bool_arr, transform=raster.transform, contour=True, contour_label_kws={}, ax=ax,
                               colors=[colour_here], linestyles=[linestyle_dict[weight]])

            if weight == '60':
                ax.scatter(max_coords[0], max_coords[1], color=colour_here, marker='o', s=30, label=line_label)

    handles, labels = ax.get_legend_handles_labels()

    line_60 = mlines.Line2D([], [], color='k', linestyle=linestyle_dict['60'], label='60%')
    line_50 = mlines.Line2D([], [], color='k', linestyle=linestyle_dict['50'], label='50%')
    line_40 = mlines.Line2D([], [], color='k', linestyle=linestyle_dict['40'], label='40%')

    handles.append(line_60)
    handles.append(line_50)
    handles.append(line_40)

    plt.legend(handles=handles, loc='upper left')
    plt.yticks(rotation=90)

    # set limits according to raster
    left_bound = min(left)
    right_bound = max(right)
    top_bound = max(top)
    bottom_bound = min(bottom)

    # ax.set_xlim(left_bound, right_bound)
    # ax.set_ylim(bottom_bound, top_bound)

    # limits which stay constant between and which suit both day's SAs
    # ax.set_xlim(279685.28503960633, 289345.4708460579)
    # ax.set_ylim(5707118.9139011325, 5716431.904868875)

    # plt.savefig('C:/Users/beths/OneDrive - University of Reading/local_runs_data/' + 'sa_lines_' + str(doy_choice) + '.png', bbox_inches='tight')

    plt.show()


sa_file_source_list = ['SCT_SWT.tif', 'BTT_BCT.tif', 'BCT_IMU.tif', 'IMU_BTT.tif']
# sa_file_source_list=['BCT_IMU.tif']

file_list_outside = find_SA_rasters(given_list=True,
                                    sa_main_dir='C:/Users/beths/OneDrive - University of Reading/Paper 2/combine_rasters/',
                                    sa_file_source=sa_file_source_list)

# colour_list = get_colours(cmap=plt.cm.inferno, file_list=file_list)
colour_list = ['green', 'blue', 'red', 'magenta']

plot_sa_lines(file_list=file_list_outside, colour_list=colour_list)


if __name__ == '__main__':

    doy_choice = 123
    sa_dir = 'C:/Users/beths/OneDrive - University of Reading/local_runs_data/fp_output/' + str(doy_choice) + '/hourly/'

    save_path = os.getcwd().replace('\\', '/') + '/'

    file_list = sa_lines.find_SA_rasters(sa_main_dir=sa_dir)
    colour_list = sa_lines.get_colours(cmap=plt.cm.inferno, file_list=file_list)
    sa_lines.plot_sa_lines(file_list=file_list, colour_list=colour_list, doy_choice=doy_choice, save_path=save_path)

    print('end')
