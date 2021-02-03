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
  
df_s1_read = pd.DataFrame({'Name': name, 'Sensing Mode', 'Product Type': product_type, 'Polarization': polarization, 'Height': height , (xxxx) display(df_s1_read)
