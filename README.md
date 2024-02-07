# CanadaUrbanMorphology
Urban Morphology parameters for the province of British Columbia (BC), Canada, to be used for WRF model

This file provides information on how to extract Urban Morphology parameters for the province of British Columbia (BC), Canada, to successfully run the Weather Research and Forecasting (WRF) model coupled with Urban Canopy Models (UCMs) with high-resolution required urban canopy parameters for Single Layer (option 1 in WRF urban physic) and Multi-layer (option 2 and 3 in WRF model, urban physic) Urban Canopy Models. In this file, "domain" refers to the domain the WRF model will be run for (e.g., d01 Or d01, d02, d03, etc. if a nested domain is used in the WRF model). "geo_em.{domain}.nc" refers to the output of the geogrid.exe program which is one of the core programs of WPS program. For a 3 nested domain, geo_em files will be annotated with the following: 'geo_em.d01.nc', 'geo_em.d02.nc', 'geo_em.d03.nc'.

This folder contains all the documents necessary for extracting the Urban Morphology parameters. Refer to Section 1 for a description of the folder structure. 

You will first need to extract the shapefile of the domain considered using the VERDI program (https://www.cmascenter.org/verdi/). For more details, refer to Section 2. Make sure to save this shapefile under the SHP subfolder described in Section 1. 

To utilize the dataset, ensure the geo_em files are placed in the 'Main' folder mentioned in Section 1, which should also contain the Python script named 'Canada_UrbanMorphology.py', the folder with the dataset (geo_em.{domain}.nc), and the folder with the shapefiles (Home_BC and domain).

The Python script 'Canada_UrbanMorphology.py' necessitates three libraries: NetCDF4, geopandas, and numpy, all of which can be installed via pip or Anaconda.  Follow the specific instructions provided in Section 3 to adjust the script, then proceed to run the program using the following command:
python3 Canada_UrbanMorphology.py
_____________________________________________________________________________________________________________________________________
Section 1. Folder structure

	Main Folder
	|- Canada_UrbanMorphology.py
	|- geo_em.{domain}.nc
	|- INT
		|- Home_BC.cpg
    		|- Home_BC.dbf
		|- Home_BC.prj
		|- Home_BC.sbn
		|- Home_BC.sbx
  		|- Home_BC.shp
		|- Home_BC.shp.xml
		|- Home_BC.shx
  	|- SHP
		|- domain.{domain}.dbf
		|- domain.{domain}.prj
		|- domain.{domain}.shp
		|- domain.{domain}.shx
		|- domain.{domain}.fix
_____________________________________________________________________________________________________________________________________
Section 2. Creating a domain shapefile

0. If you have not installed the VERDI program, follow the instructions on https://www.cmascenter.org/verdi/ to obtain the source
	code and install it.
1. Open the VERDI program.
2. On the 'Datasets' panel, click on 'add local dataset'
3. Open the desired geo_em.{domain}.nc file for the desired domain.
4. Double-click on a 2d variable (e.g., LU_INDEX) on the 'Variables' panel.
5. Click on 'Tile Plot.'
6. Click on File > Export as Image/GIS.
7. Change the 'Files of Type' to 'Shapefile (*.shp, *.shx, *.dbf).'
8. Choose the file name accordingly (i.e., geo_em.{domain}).
9. Click on Save.
10. Move the saved files to the SHP folder.

For example, to process the first domain (d01), geo_em filename would be geo_em.d01.nc and the shapefiles' name would be geo_em.d01 with GIS extentions (i.e., *.shp, *.shx, *.dbf)
_____________________________________________________________________________________________________________________________________
Section 3. Required modification to Python script

1. Adjust the grid names based on the number of nested domains used in the modeling framework (i.e., [d01, d02, d03] for a three nested domain framework) in the 'main' function, line 17.
2. Adjust the grid size (e.g., 1000*1000 for a domain with 1 km resolution) in the 'gridsize' function.
3. Check the output in the geo_em file. Due to the conversion of geo_em file to shapefile in the VERDI program, the indexing of grid cells may not be consistent between geo_em files and shapefiles. Therefore, the output after executing the Python script may look flipped (e.g., the downtown which is located in the southeast of the domain may appear in the northwest of the domain). If the output is flipped, follow the instructions on lines 163 - 170. Follow the example in the Python script to adjust the frame output.
4. Use the new geo_em files instead of previous ones for processing metgrid.exe core program in the WPS program.

Credit: Clair lab (https://cleanairlab.cive.uvic.ca/)
