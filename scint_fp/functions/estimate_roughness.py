# Beth S. 13/ 05/ 21
# script to quickly estimate the roughness length of a point using the rule of thumb, and a cropped bdsm.
# This estimate is to be used in the wx_stability script, aiming to extract params needed to run footprint calcualtion
# from wx data files (rather than relying on eddy covariance).
# roughness length is used within the calculation of ustar and L.

import rasterio
import sys
import scintools as sct
import matplotlib.pyplot as plt
import numpy as np


def crop_raster(spatial_inputs, crop_size):
    """
    Crops the bdsm raster to doimain size stated within spatial inputs.
    Parameters
    ----------
    spatial_inputs: Sct object

    Returns
    -------
    Cropped bdsm
    """
    # Load rasters and crops to centre point of source area.
    open_raster = rasterio.open(spatial_inputs.bdsm_path)

    # Take raster files as an arrays
    raster_array = open_raster.read(1)

    focus_point_pixel = open_raster.index(
        spatial_inputs.x, spatial_inputs.y)  # index of focus point by row, col

    # Check to see if focus point is within the rasters
    point_row = focus_point_pixel[0]
    point_col = focus_point_pixel[1]
    raster_arr_rows = raster_array.shape[0]
    raster_arr_cols = raster_array.shape[1]

    if point_row < 0 or point_col < 0 or point_row > raster_arr_rows or point_col > raster_arr_cols:
        print(' ')
        print('Index of focus point is outside of raster arrays: ')
        print('focus point index: ', focus_point_pixel)
        print('raster shape: ', raster_array.shape)
        print('Please choose a raster containing chosen point,')
        print('Or choose a focus point within the raster.')
        sys.exit()

    domain_pixels = crop_size / spatial_inputs.domain_res

    # define area of model to run
    # attribute central location where Site is positioned and crop around that area
    r = domain_pixels / 2

    # check to see if extension defined by r around the focus point is still within the bounds of the raster
    row_extension_positive = point_row + r
    row_extension_negative = point_row - r
    col_extension_positive = point_col + r
    col_extension_negative = point_col - r

    if row_extension_positive > raster_arr_rows or row_extension_negative < 0 or \
            col_extension_positive > raster_arr_cols or col_extension_negative < 0:
        print(' ')
        print('Model domain size chosen: ')
        print(spatial_inputs.domain_size)
        print('is too large for the current size of the raster: ')
        print(raster_array.shape)
        print('This could be due to where the focus point is located in the raster.')
        print('Please reduce the model domain size.')
        sys.exit()

    raster_crop = (raster_array[
                   int(row_extension_negative):int(row_extension_positive),
                   int(col_extension_negative):int(col_extension_positive)])

    open_raster.close()

    return raster_crop


def calculate_quick_roughness(spatial_inputs, crop_size):
    """
    Estimatea roughness length and displacement height  from mean building using the rule of thumb method,
        for a cropped bdsm.
    Parameters
    ----------
    spatial_inputs: Sct object

    Returns
    -------
    Estimate of roughness params z_0 and z_d
    """
    # crop raster
    cropped_raster = crop_raster(spatial_inputs, crop_size)

    # mean building height
    z_h = np.mean(cropped_raster)

    roughness = sct.roughness_methods.rt(z_h)

    return roughness
