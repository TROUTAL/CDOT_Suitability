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

# setting workspace and environmental parameters
env.workspace = r'D:\Programming\Suitability_project\data_with'
boundary = 'Project_Bounds.shp'
env.extent = boundary 
env.mask = boundary 
env.overwriteOutput = 1

# This function takes a suitability array and calculates the area for each suitability zone
def ZoneStats (ValueArray):
    zones = np.unique(ValueArray)
    for i in zones[1:]:
        flat = ValueArray.ravel()
        number = np.where(flat == i, flat, 0)
        suit = number[number != 0]
        suit_count = suit.shape[0]
        acres = (suit_count * 900) * 0.00025
        print('Zones with a suitability of:',i,'have a coverage of', round(acres, 2), 'acres')

# List of the inputs clipped to the projected boundary 
clip_results = ['proj_roads.shp', 'proj_habitat.shp', 'proj_wetlands.shp', 'proj_dem.tif']

# setting distance (meters) parameters for reclassification
wet_dist = 120
roads_dist = 90
habitat_dist = 120

'''
This block of code runs Euclidean distance for each of the 3 shapefiles and
converts them to numpy arrays. Once as numpy arrays they are reclassified based
upon their distance parameters. The DEM raster is converted to a slope raster
and reclassifed upon slope parameters. Arrays are added to create suitability
raster. While loop runs through this process twice testing wetlands distance.
'''
suit_list = []
counter = 0
while counter <= 1:
    ras_arrays = []
    for r in clip_results:
        if r == 'proj_roads.shp':
            dist = arcpy.sa.EucDistance(r, '', 30)
            dist.save('roads_buff.tif')
            ras = arcpy.RasterToNumPyArray('roads_buff.tif')
            rasReclass = np.where(ras > roads_dist, 1, 0)
            sheared = np.delete(rasReclass, 2108, 1)
            ras_arrays.append(sheared)
        elif r == 'proj_habitat.shp': 
            dist = arcpy.sa.EucDistance(r, '', 30)
            dist.save('habitat_buff.tif')
            ras = arcpy.RasterToNumPyArray('habitat_buff.tif')
            rasReclass = np.where(ras > habitat_dist, 0, 1)
            sheared = np.delete(rasReclass, 2108, 1)
            ras_arrays.append(sheared)
        elif r == 'proj_wetlands.shp': 
            dist = arcpy.sa.EucDistance(r, '', 30)
            dist.save('wetlands_buff.tif')
            ras = arcpy.RasterToNumPyArray('wetlands_buff.tif')
            rasReclass = np.where(ras > wet_dist, 0, 1)
            sheared = np.delete(rasReclass, 2108, 1)
            ras_arrays.append(sheared)
        elif r == 'proj_dem.tif':
            dist = arcpy.sa.Slope(r, 'PERCENT_RISE')
            dist.save('slope.tif')
            array = arcpy.RasterToNumPyArray('slope.tif')
            ras = np.where(array > 4, 1, 0)
            ras_arrays.append(ras)
    suitras = ras_arrays[0] + ras_arrays[1] + ras_arrays[2] + ras_arrays[3]
    ZoneStats(suitras)
    suit_list.append(suitras)
    wet_dist = wet_dist - 60
    counter = counter + 1
       
# Writing the added numpy array to a raster
ras = rasterio.open(r'D:\Programming\Suitability_project\data_with\habitat_buff.tif')
meta = ras.meta 

# Writing the added numpy array to a raster 
with rasterio.open(r'D:\Programming\Suitability_project\data_with\Suitability120.tif', 'w', **meta) as dest:
    dest.write(suit_list[0].astype('float32'), indexes=1)

with rasterio.open(r'D:\Programming\Suitability_project\data_with\Suitability60.tif', 'w', **meta) as dest:
    dest.write(suit_list[1].astype('float32'), indexes=1)

# Setting variables to Pueblo and FT Collins train station shapefiles 
Collins_station = 'FTCollins_station.shp'
Pueblo_station = 'Pueblo_station.shp'


# Running cost distance function with suitability outcomes and city train stations
CollinsCost = arcpy.sa.CostDistance(Collins_station, 'Suitability120.tif')
CollinsCost.save('ColCost120.tif')
PuebloCost = arcpy.sa.CostDistance(Pueblo_station, 'Suitability120.tif')
PuebloCost.save('PueCost120.tif')

# Running Corridor analysis to create final product 
Corr120 = arcpy.sa.Corridor('ColCost120.tif', 'PueCost120.tif')
Corr120.save('Corridor120.tif')


    