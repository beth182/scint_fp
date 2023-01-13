# Beth Saunders 13/01/23
# split landcover dataset into sectors by angle and calculate land cover fraction

# imports
from osgeo import gdal
from gdalconst import GA_ReadOnly
import os
import rasterio
import numpy as np

import matplotlib.pyplot as plt


def lc_by_sector(image,
                 transform,
                 save_path,
                 landcover_location='C:/Users/beths/OneDrive - University of Reading/Model_Eval/QGIS/Elliott/LandUseMM_7classes_32631.tif'):
    print('end')

    # crop square extent of landcover fractions file to the same as the
    maskDs = gdal.Open(SA_file, GA_ReadOnly)  # your mask raster
    projection = maskDs.GetProjectionRef()
    geoTransform = maskDs.GetGeoTransform()
    minx = geoTransform[0]
    maxy = geoTransform[3]
    maxx = minx + geoTransform[1] * maskDs.RasterXSize
    miny = maxy + geoTransform[5] * maskDs.RasterYSize
    data = gdal.Open(landcover_location, GA_ReadOnly)

    # Your data the one you want to clip
    output = save_path + 'output.tif'  # output file
    gdal.Translate(output, data, format='GTiff', projWin=[minx, maxy, maxx, miny], outputSRS=projection)

    # reads this cropped dataset
    landcover_crop = rasterio.open(output)
    landcover_array = landcover_crop.read(1)

    # test of two arrays have the same shape
    if sa_array.shape == landcover_array.shape:
        pass
    else:
        if landcover_array.shape == sa_array[0:sa_array.shape[0] - 1, 0:sa_array.shape[1] - 2].shape:
            sa_array = sa_array[0:sa_array.shape[0] - 1, 0:sa_array.shape[1] - 2]
        elif landcover_array.shape == sa_array[0:sa_array.shape[0] - 1, 0:sa_array.shape[1] - 1].shape:
            # remove last row/col
            sa_array = sa_array[0:sa_array.shape[0] - 1, 0:sa_array.shape[1] - 1]
        else:
            assert sa_array.shape == landcover_array.shape

    mask = np.ma.masked_where(np.isnan(sa_array), landcover_array, copy=True)

    print('end')
