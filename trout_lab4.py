"""*********************************************
author: Alex Trout
Date: 10/17/19
Purpose: Lab 4
*********************************************"""

# Part I 

# importing modules
import numpy as np
import arcpy
from arcpy import env
import rasterio
from scipy.spatial import cKDTree

# setting environments
arcpy.CheckOutExtension('Spatial')
env.workspace = r'D:\Programming\lab4\lab4\data'
env.overwriteOutput = 1

# setting raster variables
protected = 'protected_areas.tif'
slope = 'slope.tif'
urban = 'urban_areas.tif'
water = 'water_bodies.tif'
wind = 'ws80m.tif'
# cell size: 1000 meters (1 KM)

# lists holding tif files and parameter arrays 
ras_list = [protected, slope, urban, water, wind]
ParaList = []

# loop through each tif raster and create Numpy array
for raster in ras_list:
    rasArray = arcpy.RasterToNumPyArray(raster)
    ParaArray = np.zeros_like(rasArray, dtype=np.float32)
    np.where(rasArray < 0, 0, rasArray)
    for row in range(5, rasArray.shape[0] - 5):
        for col in range(4, rasArray.shape[1] - 4):
            window = rasArray[row - 5:row + 6, col - 4:col + 5]
            if raster == protected:
                ParaArray[row, col] = window.sum()
            elif raster == water:
                ParaArray[row, col] = window.sum()
            else:
                ParaArray[row, col] = window.mean()
    ParaList.append(ParaArray)

# converting protected array to boolean
proSites = np.where(ParaList[0] < 0.05, 1, 0)

# converting slope array to boolean
sloSites = np.where(ParaList[1] < 15, 1, 0)

# converting urban array to boolean
urbSites = np.where(ParaList[2] == 0, 1, 0)

# converting water array to boolean 
watSites = np.where(ParaList[3] < 0.02, 1, 0)

# converting wind array to boolean
winArray = np.where(ParaList[4] > 8.5, 1, 0)
winSites = np.where(ParaList[4] > 11, 0, winArray)

# print statement giving the count of identified suitable sites 
suitSites = (proSites + sloSites + urbSites + watSites + winSites)
print(np.where(suitSites == 5)[0].size, 'sites were identified as suitable for the given parameters')

# writing suitable sites array to .tif file using the meta data from the existing slope raster 
ras = rasterio.open('D:\Programming\lab4\lab4\data\slope.tif')
meta = ras.meta 
with rasterio.open('D:\Programming\lab4\lab4\data\suitSites.tif', 'w', **meta) as dest:
    dest.write(suitSites.astype('float32'), indexes=1)

# Part II

# identifying the coordinates for centroids of each suitable site 
# opening suitable sites raster and obtaining the boundaries, the upper left, and lower right extents of the raster
ras1 = rasterio.open('D:\Programming\lab4\lab4\data\suitSites.tif')
bounds1 = ras1.bounds
upLeft = [bounds1[0], bounds1[3]]
botRight = [bounds1[2], bounds1[1]]
cellsize = 1000

# reshapes centroids array to mirror suitSites array
# replaces every Suitable site in suitSites array with the correspoding centroid
# non suitable sites are converted to 0 and then removed
# an array with just the centroids of suitable sites is returned
def Suitcentroids(suits, cents):
    shapedcent = cents.reshape(1765, 1121)
    Suitroid = np.where(suits == 5, shapedcent, 0)
    Suitroid = Suitroid[Suitroid != 0]
    return Suitroid

# grabbing the centroids for each cell and obtaining coordinates for these centroids 
# inputing centroids and suitSites array into custom fuction
xCoordinates = np.arange(upLeft[0] + cellsize / 2, botRight[0], cellsize)
yCoordinates = np.arange(botRight[1] + cellsize / 2, upLeft[1], cellsize)
x, y = np.meshgrid(xCoordinates, yCoordinates)
Xcentroids = np.c_[x.ravel()]
Ycentroids = np.c_[y.ravel()]
suitroidX = Suitcentroids(suitSites, Xcentroids)
suitroidY = Suitcentroids(suitSites, Ycentroids)

# creating sub-station points from the coordinates text file and placing them into raveled array
txt_file = env.workspace + '/transmission_stations.txt'
with open(txt_file) as file:
    lines01 = file.readlines()
    i = 1
    Xcoord = []
    Ycoord = []
    while i < len(lines01):
        XS = lines01[i].split(',')
        Xcoord.append(float(XS[0]))
        Ycoord.append(float(XS[1]))
        i = i + 1
    XSub = np.asarray(Xcoord)
    YSub = np.asarray(Ycoord)

# stacking and transposing inputs for cKDTree function
targetPnts = np.vstack([suitroidX, suitroidY]).T
sourcePnts = np.stack([XSub, YSub]).T
dist, indices = cKDTree(targetPnts).query(sourcePnts)
print('The minimum distance is', round(dist.min() / 1000, 2), 'kilometers, & the maximum distance is', round(dist.max() / 1000, 2), 'kilometers')

  


