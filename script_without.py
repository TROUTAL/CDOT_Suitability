# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 10:32:55 2019

@author: Ian Heckman, Matt Berns, & Alex Trout
"""
# importing libraries 
import arcpy 
from arcpy import env
from arcpy.sa import *
import os
import rasterio 
import numpy as np

# setting workspace 
env.workspace = r'D:\Programming\Suitability_project\data_with'
boundary = 'Project_Bounds.shp'
env.extent = boundary 
env.mask = boundary 
env.overwriteOutput = 1 


clip_results = ['proj_roads.shp', 'proj_habitat.shp', 'proj_wetlands.shp', 'proj_dem.tif']
ras_arrays = []

# running euclidean distance function for each input
# reclassifying euclidean distance outputs
for r in clip_results:
    if r == 'proj_roads.shp':
        dist = arcpy.sa.EucDistance(r, '', 30)
        dist.save('roads_buff.tif')
        ras = arcpy.RasterToNumPyArray('roads_buff.tif')
        rasReclass = np.where(ras > 90, 0, 1)
        ras_arrays.append(rasReclass)
    elif r == 'proj_habitat.shp': 
        dist = arcpy.sa.EucDistance(r, '', 30)
        dist.save('habitat_buff.tif')
        ras = arcpy.RasterToNumPyArray('habitat_buff.tif')
        rasReclass = np.where(ras > 120, 1, 0)
        ras_arrays.append(rasReclass)
    elif r == 'proj_wetlands.shp': 
        dist = arcpy.sa.EucDistance(r, '', 30)
        dist.save('wetlands_buff.tif')
        ras = arcpy.RasterToNumPyArray('wetlands_buff.tif')
        rasReclass = np.where(ras > 120, 1, 0)
        ras_arrays.append(rasReclass)
    elif r == 'proj_dem.tif':
        dist = arcpy.sa.Slope(r, 'PERCENT_RISE')
        dist.save('slope.tif')
        ras = arcpy.RasterToNumPyArray('slope.tif')
        rasArrays = np.where(ras > 4, 0, 1)
        ras_arrays.append(rasArrays)

for tit in ras_arrays:
    print(tit.max(), tit.min(), tit.shape)
    
# adding arrays together to get suitable areas array
suitras = ras_arrays[0] + ras_arrays[1] + ras_arrays[2] + ras_arrays[3]


# Writing the added numpy array to a raster
ras = rasterio.open(r'D:\Programming\Suitability_project\data_with\habitat_buff.tif')
meta = ras.meta 

# Writing the added numpy array to a raster 
with rasterio.open(r'D:\Programming\Suitability_project\data_with\Suit_Corridors.tif', 'w', **meta) as dest:
    dest.write(suitras.astype('int32'), indexes=1)



    