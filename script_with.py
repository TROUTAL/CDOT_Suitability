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

unclipped_shps = ['Highways.shp', 'Critical_habitat.shp', 'Wetlands.shp']
clip_results = ['proj_roads.shp', 'proj_habitat.shp', 'proj_wetlands.shp']
dists = ['roads_dist', 'habitat_dist', 'wetlands_dist', 'proj_slope']
buffered = ['roads_buff', 'habitat_buff', 'wetlands_buff', 'slope']

# clipping each input feature to the project boundaries 
# appending wetlands clipped file to clipped list as it was already clipped
for u, c in zip(unclipped_shps, clip_results): 
    arcpy.Clip_analysis(u, boundary, c)

# the DEM raster must be clipped using a different method, appended to clip_results
extract = arcpy.sa.ExtractByMask('dem.tif', boundary)
extract.save('proj_dem.tif')
clip_results.append('proj_dem.tif')

# running euclidean distance function for each input
# reclassifying euclidean distance outputs
for r, d, b in zip(clip_results, dists, buffered):
    if r == 'project_roads.shp':
        d = arcpy.sa.EucDistance(r, 300000, 30)
        reclassify = arcpy.sa.Reclassify(d, 'Value', RemapRange([[0, 90, 1], [90, 300000, 0]]))
        reclassify.save(b)
    elif r == 'proj_habitat.shp': 
        d = arcpy.sa.EucDistance(r, 300000, 30)
        reclassify = arcpy.sa.Reclassify(d, 'Value', RemapRange([[0, 510, 0], [510, 300000, 1]]))
        reclassify.save(b)
    elif r == 'proj_wetlands.shp': 
        d = arcpy.sa.EucDistance(r, 300000, 30)
        reclassify = arcpy.sa.Reclassify(d, 'Value', RemapRange([[0, 120, 0], [120, 300000, 1]]))
        reclassify.save(b)
    elif r == 'proj_dem.tif':
        d = arcpy.sa.Slope(r, 'PERCENT_RISE')
        d.save(b)
        
# copying the rasters created in the Euclidean Distance function and copying them to a TIFF file
# converting TIFF file to numpy array and appending them to a list 
ras_arrays = []
for GRID in buffered:
    tif = arcpy.CopyRaster_management(GRID, str(GRID) + '.tif')
    NumpyArray = arcpy.RasterToNumPyArray(GRID)
    ras_arrays.append(NumpyArray)
    
for i in ras_arrays:
    suitras = np.sum(ras_arrays[0:]) # Attempting to add all numpy rasters together in ras_arrays list. Don't think it's working.

# Writing the added numpy array to a raster
ras = rasterio.open(r'D:\Programming\Suitability_project\data_with\habitat_buff.tif')
meta = ras.meta 

# Writing the added numpy array to a raster 
with rasterio.open(r'D:\Programming\Suitability_project\data_with\Suit_Corridors.tif', 'w', **meta) as dest:
    dest.write(suitras.astype('uint8'), indexes=1)
