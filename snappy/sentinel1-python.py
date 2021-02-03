#Code copied from RUS webinar, youtube video PY01, rus-training.eu was down.

import matplotlib.colors as colors #create visualizations
import matplotlib.image as mpimg   #create visualizations
import matplotlib.pyplot as plt    #create visualizations
from termcolor import colored      #prints colored text
from zipfile import ZipFile        #zip file manipulation
from os.path import join           #data access in file manager
from glob import iglob             #data access in file manager
import pandas as pd                #data analysis and manipulation
import numpy as np                 #scientific computing
import subprocess                  #external calls to system
import snappy                      #SNAP python interface
import jpy                         #Python-Java bridge (SNAP is implemented in Java)

#Change module setting of pandas
pd.options.display.max_colwidth = 80 #Longer text in pd.df

#User-defined functions

def output_view(product, band, min_value_VV, max_value_VV, min_value_VH, max_value_VH):
  """
  Creates visualization of processed Sentinel-1 SAR data
  
  Keyword arguments:
  product        -- snappy GPF product --> input Sentinel-1 product
  band           -- List --> product's band to be visualized
  min_value_VV   -- int --> min value for color strech in VV band
  max_value_VV   -- int --> max value for color strech in VV band
  min_value_VH   -- int --> min value for color strech in VH band
  max_value_VH   -- int --> max value for color strech in VH band
  """
  band_data_list = []
  
  for i in band:
    band = product.getBand(i)
    w = band.getRasterWidth()
    h = band.getRasterHeight()
    band_data = np.zeros(w * h, np.float32)
    band.readPixels(0, 0, w, h, band_data)
    band_data.shape = h, w
    band_data_list.append(band_data)
    
    fig, (ax1,ax2) = plt.subplots(1,2, figsize=(16,16))
    ax1.imshow(band_data_list[0], cmap='gray', vmin=min_value_VV , vmax=max_value_VV)
    ax1.set_title(output_bands[0])
    ax2.imshow(band_data_list[1], cmap='gray', vmin=min_value_VH , vmax=max_value_VH)
    ax2.set_title(output_bands[1])
    
    for ax in fig.get_axes():
      ax.label_outer()
      
#Sentinel-1 Preporocessing: snappy

#Call gpt -h from command line to see operators available in snappy. for specific operator call "gpt -h *operator*"
print(subprocess.Popen(['gpt', '-h', 'ThermalNoiseRemoval'], stdout=subprocess.PIPE, universal_newlines=True).communicate()[0])
                       
#Stepps of pre-processing to generate analysis-ready data:
#Read->Subset->Apply Orbit File->Thermal Noise Removal->Calibration->Speckle Filtering->Terrain Correction->Write

#Read Product
#Set target folder and extract metadata
product_path = "/shared/Training/PY01_SentinelProcessing_snappy/Original" #Change this path with the source folder (source file in .zip)
input_S1_files = sorted(list(iglob(join(product_path, '**', '*S1*.zip'), recursive=True)))

name, sensing_mode, produt_type, polarization, height, width, band_names = ([] for i in range (7))

for i in input_S1_files:                        #extracting metadata from the product name
  sensing_mode.append(i.split("_")[3])
  product_type.append(i.split("_")[4])
  polarization.append(i.split("_")[-6])
  #REad with snappy
  s1_read = snappy.ProductIO.readProduct(i)
  name.append(s1_read.getName())
  height.append(s1_read.getSceneRasterHeight())
  width.append(s1_read.getSceneRasterWidth())
  band_names.append(S1_read.getBandNames())
  
df_s1_read = pd.DataFrame({'Name': name, 'Sensing Mode', 'Product Type': product_type, 'Polarization': polarization, 'Height': height , (xxxx)})
display(df_s1_read) #not completed dictionary, they are not visible in the YT video

#Display quicklook - First image
with ZipFile(input_S1_files[0], 'r') as qck_look:
  qck_look = qck_look.open(name[0] + '.SAFE/preview/quick-look.png') #extracts a specific file inside the zipfile using python zipfile module.
  img = mpimg.imread(qck_look)
  plt.figure(figsize = (15,15))
  plt.title('Quicklook visulization - '+ name[0] + '\n')
  plt.axis('off')
  plt.imshow(img);
  
#Subset
 #Defining the Area Of Interest (AOI), defining pixels coordinates, less processing time.
  
#ur corner
x, y, width, height = 12000, 8000, 5500, 5500
  
#Subset Operator - snappy
parameters = snappy.HashMap()
parameters.put('copyMetadata', True)
parameters.put('region', "%s,%s,%s,%s" % (x, y, width, height))
subset = snappy.GPF.createProduct('Subset', parameters, s1_read) #calls operator of snappy
list(subset.getBandNames())

#Plot subset (follow VV - VH order)
output_bands = ['Amplitude_VV', 'Amplitude_VH']
output_view(subset, output_bands, 41, 286, 20, 160) #Try and error values, treshold affect the view output
 
#Apply orbit file
parameters = snappy.HashMap()
parameters.put('Apply-Orbit-File'. True)
apply_orbit = snappy.GPF.createProduct('Apply-Orbit-File', parameters, subset)
print(colored('Orbit updated succesfully', 'green'))
 
#Thermal Noise Removal from the image generated by the sensor noise.
#Thermal noise removal operator in snappy
parameters = snappy.HashMap()
parameters.put('removeThermalNoise', True)
thermal_noise = snappy.GPF.creatProduct('ThermalNoiseRemoval', parameters, apply_orbit)

#Plot thermal noise removal (follow vv - vh order)
output_bands = ['Intensity_VV', 'Intensity_VH']
output_view(thermal_noise, output_bands, 0.02, 99376.52,  0.27, 8471.83)

#Radiometric Calibration
#Needed for quantitatibve use of SAR data.
#Need to be done in user-side with Level-1 images.
#Calibration Operator - snappy
parameters = snappy.HashMap()
parameters.put('outputSigmaBand', True)
parameters.put('sourceBands', 'Itensity_VH, Itensity_VV')
parameters.put('selectdPolarisations', 'VH, VV')
parameters.put('outputImageScaleInDb', False)
calibrated = snappy.GPF.createProduct("Calibration", parameters, thermal_noise)

#Plot Calibration (follow VV - VH order)
output_bands = ['Sigma0_VV', 'Sigma0_VH']
output_view(calibrated, output_bands, 0.00, 0.28, 0.00, 0.05)

#Speckle Filtering
#Speckle noise reduction by spatial filtering or multilook processing.
#GORD product are already multi looped
# additional multi looping -->reduse spectral filter but also lose spatial resolution
# spatial filtering --> Not loose spatial resolution But original pixel values will change.

#Speckle Filtering Operator - snappy
parameters = snappy.HashMap()
parameters.put('filter'. 'Lee')
parameters.put('filterSizeX', 5)
parameters.put('filterSizeY', 5)
speckle = snappy.GPF.createProduct('Speckle-Filter', parameters, calibrated)

#Plot speckle filter (follow VV - VH order)
output_bands = ['Sigma0_VV', 'Sigma0_VH']
output_view(speckle, output_bands, 0.00, 0.21, 0.00, 0.048)

#Terrain Correction
#In SAR images, distances can be distorted.

#Create variable of the projection with information
#SNAP GUI feature --> automatically detets the UTM zone in the terrain correction operator
#ToDo: Find a way to extract this information automatically from xlm file...
proj = '''PROJCS["UTM Zone 31 / World Geodetic System 1984",
  GEOGCS["World Geodetic System 1984",
    DATUM["World Geodetic System 1984",
      SPHEROID["WGS 84", 6378137.0, 298.257223563, AUTHORITY["EPSG", "7030"]],
      AUTHORITY["EPSG", "6326"]],
    PRIMEM["Greenwich", 0.0, AUTHORITY["EPSG", "8901"]],
    UNIT["degree", 0.017453292519943295],
    AXIS["Geodetic longitude", EAST],
    AXIS["Geodetic longitude", north]],
  PROJECTION["Transverse_Mercator"],
  PARAMETER["central_meridian", 3.0],
  PARAMETER["latitude_of_origin", 0.0],
  PARAMETER["scale_factor", 0.9996],
  PARAMETER["false_easting", 500000.0],
  PARAMETER["false_northing", 0.0],
  UNIT["m", 1.0],
  AXIS["Easting", EAST],
  AXIS["Northing", NORTH]]'''

#Terrain-Correction Operator - snappy
parameters = snappy.HashMap()
parameters.put('demName', 'SRTM 3Sec')
parameters.put('imgResamplingMethod', 'BILINEAR_INTERPOLATION')
parameters.put('pixelSpacingInMeter', 10.0)
parameters.put('mapProjection', proj)
parameters.put('nodataValueAtSea', False) # do not mask areas without elevation
parameters.put('saveSelectedSourceBand', True)
terrain_correction = snappy.GPF.createProduct('Terrain-Correction', parameters, speckle)

#Plot terrain correction (follow VV - VH order)
output_bands = ['Sigma0_VV', 'Sigma0VH'] # in this step Amplitude bands are lost?
output_view(terrain_correction, output_bands, 0.00, 0.49, 0.00, 0.04)

#Write



