Overview

This program computes PGA prediction results (GeoTIFF format) based on selected GMPEs by providing basic earthquake information and Vs30 data. The workflow is designed for rapid, flexible ground‐motion estimation in regions with user-defined input parameters.

Functionality

Users input basic earthquake parameters (e.g., magnitude, coordinates, depth).

Vs30 can be directly supplied using a global Vs30 model; the program will automatically clip the Vs30 dataset to the specified radius around the epicenter.

The program outputs predicted PGA maps in .tif format for each selected GMPE.

The GMPE module is fully customizable—new models can be added or existing ones modified.

Program Structure

main_gui.py：Graphical user interface. Run this file to start the program.

GMPE.py：Contains all implemented GMPE functions. Modify this file to add or update GMPE models.

Ensure all files are placed in the same directory if running from a local Python environment.

Environment

The program was developed and tested under Python 3.12.

Dependencies

The following packages are required:

numpy  
rasterio  
pyproj  
# Tkinter is built-in with standard Python, no installation required


Install dependencies using:

pip install numpy rasterio pyproj

Usage

Prepare earthquake parameters and Vs30 raster file.

Run main_gui.py.

Select GMPE(s) to use.

The program will automatically crop Vs30 to the specified distance around the epicenter.

The final PGA predictions will be exported as .tif files.
