import geopandas as gpd
import numpy as np
from netCDF4 import Dataset
import os

###########################################################
## Credit to Clair lab https://cleanairlab.cive.uvic.ca/ ##
## Forood Azargoshasbi (fazargoshasbi@uvic.ca)           ##
## Laura Minet         (lauraminet@uvic.ca)              ##
###########################################################

def main():
    print('Start of program...')
    # Creating the OUTPUT foder
    if not os.path.exists('./Out'): os.mkdir('./Out')
    database = transform()
    for dm in ['d04', 'd03', 'd02', 'd01', ]: #### Change base on your domain names
        print(dm)
        
        #### Reading files and calculating the data
        dfG = gpd.read_file(f'./SHP/geo_em.{dm}.shp') # domain grid shapefile        
        # Intersecting the domain grid shapefile with housing shapefile.
        dfD = intersct(dm, homes=database, domain=dfG)

        dfD.drop(columns=['geometry'], inplace=True)
        for i, j in zip(range(0, 75, 5), range(5, 80, 5)):
            if i == 70: mask = dfD['HGT'] >= i
            else: mask = np.logical_and(dfD['HGT'] >= i, dfD['HGT'] < j)
            dfD.loc[mask, 'B_cat'] = j
        dfD['areaXh'] = dfD['bldgarea'] * dfD['HGT'] # This paramter is required later to calculate WMBH

        C_df = dfD.groupby(['FID_geo_em', 'B_cat'])
        tttt = C_df.count().reset_index(level=[1])
        ttvv = tttt.groupby('FID_geo_em').sum()
        for index in ttvv.index:
            tttt.loc[index, 'Total_Count'] = ttvv.at[index, 'HGT']
        tttt['Build_hito'] = tttt['HGT'] / tttt['Total_Count']

        ttttm = dfD.groupby(['FID_geo_em'])
        dfDm = ttttm.mean()   # grouping by geo_em indexes (average)
        dfDs = ttttm.std()    # grouping by geo_em indexes (standard deviation)
        dfDx = ttttm.sum()    # grouping by geo_em indexes (sum)
        
        dfVx = dfD.groupby(['FID_geo_em', 'B_cat']).sum().reset_index(level=[1])

        #allocating values from intersection shapefile to domain grid shapefile
        for index in dfDm.index:
            dfG.at[index, 'HGT']        = dfDm.at[index, 'HGT']
            dfG.at[index, 'STD']        = dfDs.at[index, 'HGT']
            dfG.at[index, 'WMBH']       = dfDx.at[index, 'areaXh'] / dfDx.at[index, 'bldgarea']
            dfG.at[index, 'PAF']        = dfDx.at[index, 'bldgarea'] / gridsize(dm)
            dfG.at[index, 'f0']         = dfDx.at[index, 'f0'] / gridsize(dm)
            dfG.at[index, 'f45']        = dfDx.at[index, 'f45'] / gridsize(dm)
            dfG.at[index, 'f90']        = dfDx.at[index, 'f90'] / gridsize(dm)
            dfG.at[index, 'f135']       = dfDx.at[index, 'f135'] / gridsize(dm)
            dfG.at[index, 'BStPA']      = dfDx.at[index, 'Surf'] / dfDx.at[index, 'bldgarea']
            dfG.at[index, 'CAR']        = (dfDx.at[index, 'Surf'] / gridsize(dm)) + 1
            for ii, jj in enumerate(range(5, 80, 5)):
                # Building Height distribution
                mask = np.logical_and(tttt.index == index, tttt['B_cat'] == jj)
                val = tttt.loc[mask, 'Build_hito']
                if val is float:
                    val = val
                elif len(val) > 0:
                    val = val.values[0]
                else:
                    val = 0
                dfG.at[index, f'B_H_{ii}'] = val

                # frontal area 0
                mask = np.logical_and(dfVx.index == index, dfVx['B_cat'] == jj)
                val = dfVx.loc[mask, 'f0']
                if val is float:
                    val = val
                elif len(val) > 0:
                    val = val.values[0]
                else:
                    val = 0
                dfG.at[index, f'f0_{ii}'] = val / dfDx.at[index, 'f0']
                
                # frontal area 45
                val = dfVx.loc[mask, 'f45']
                if val is float:
                    val = val
                elif len(val) > 0:
                    val = val.values[0]
                else:
                    val = 0
                dfG.at[index, f'f45_{ii}'] = val / dfDx.at[index, 'f0']

                # frontal area 90
                val = dfVx.loc[mask, 'f90']
                if val is float:
                    val = val
                elif len(val) > 0:
                    val = val.values[0]
                else:
                    val = 0
                dfG.at[index, f'f90_{ii}'] = val / dfDx.at[index, 'f0']

                # frontal area 135
                val = dfVx.loc[mask, 'f135']
                if val is float:
                    val = val
                elif len(val) > 0:
                    val = val.values[0]
                else:
                    val = 0
                dfG.at[index, f'f135_{ii}'] = val / dfDx.at[index, 'f0']

                # Plan Area density
                val = dfVx.loc[mask, 'bldgarea']
                if val is float:
                    val = val
                elif len(val) > 0:
                    val = val.values[0]
                else:
                    val = 0
                dfG.at[index, f'PAD_{ii}'] = val / dfDx.at[index, 'bldgarea']
                
        # Saveing the output shapefile
        dfG.to_file(f'./Out/f{dm}.shp')

        # Assign 0 to un-urban grid cells for all parameters.
        for col in ['HGT', 'STD', 'WMBH', 'PAF', 'f0', 'f45', 'f90', 'f135', 'BStPA', 'CAR']:
            dfG.loc[dfG[col].isnull(), col] = 0
        for id_ in range(15):
            dfG.loc[dfG[f'B_H_{id_}'].isnull(), f'B_H_{id_}'] = 0
            dfG.loc[dfG[f'f0_{id_}'].isnull(), f'f0_{id_}'] = 0
            dfG.loc[dfG[f'f45_{id_}'].isnull(), f'f45_{id_}'] = 0
            dfG.loc[dfG[f'f90_{id_}'].isnull(), f'f90_{id_}'] = 0
            dfG.loc[dfG[f'f135_{id_}'].isnull(), f'f135_{id_}'] = 0
            dfG.loc[dfG[f'PAD_{id_}'].isnull(), f'PAD_{id_}'] = 0
        
        # Opening the geo_em.d##.nc file
        nc = Dataset(f'./geo_em.{dm}.nc', 'r+')
        urb_temp = nc['URB_PARAM'][:]
        lu_ = nc['LU_INDEX'][0]
        frc = nc['FRC_URB2D'][0]
        #creating a temporary output file and assigning calculated urban morphology to different index
        temp = np.zeros(nc['URB_PARAM'].shape)
        shp = (temp.shape[2], temp.shape[3])
        
        temp[0,90,:,:] = dfG['PAF'].to_numpy().reshape(shp)     # Plan area fraction
        temp[0,91,:,:] = dfG['HGT'].to_numpy().reshape(shp)     # Mean Building Height
        temp[0,92,:,:] = dfG['STD'].to_numpy().reshape(shp)     # Standard Deviation of Building Height
        temp[0,93,:,:] = dfG['WMBH'].to_numpy().reshape(shp)    # Area Weighted Mean Building Height
        temp[0,94,:,:] = dfG['BStPA'].to_numpy().reshape(shp)   # Building Surface to Plan Area Ratio
        temp[0,95,:,:] = dfG['f0'].to_numpy().reshape(shp)      # Frontal Area Index (Wind Direction=0)
        temp[0,96,:,:] = dfG['f45'].to_numpy().reshape(shp)     # Frontal Area Index (Wind Direction=45)
        temp[0,97,:,:] = dfG['f90'].to_numpy().reshape(shp)     # Frontal Area Index (Wind Direction=90)
        temp[0,98,:,:] = dfG['f135'].to_numpy().reshape(shp)    # Frontal Area Index (Wind Direction=135)
        temp[0,99,:,:] = dfG['CAR'].to_numpy().reshape(shp)     # Complete Aspect Ratio
        for id_ in range(15):
            temp[0,117+id_,:,:] = dfG[f'B_H_{id_}'].to_numpy().reshape(shp)  # Building Height Histogram
            temp[0,id_,:,:]     = dfG[f'f0_{id_}'].to_numpy().reshape(shp)   # Frontal area density (Wind Direction=0)
            temp[0,15+id_,:,:]  = dfG[f'f135_{id_}'].to_numpy().reshape(shp) # Frontal area density (Wind Direction=135)
            temp[0,30+id_,:,:]  = dfG[f'f45_{id_}'].to_numpy().reshape(shp)  # Frontal area density (Wind Direction=45)
            temp[0,45+id_,:,:]  = dfG[f'f90_{id_}'].to_numpy().reshape(shp)  # Frontal area density (Wind Direction=90)
            temp[0,60+id_,:,:]  = dfG[f'PAD_{id_}'].to_numpy().reshape(shp)  # Plan Area Density
            temp[0,75+id_,:,:]  = dfG[f'PAD_{id_}'].to_numpy().reshape(shp)  # Roof Area Density

        ######################################################################################
        # Check the Output for each domain netcdf file. If the Output seems oriented,        #
        # you have to use similar script to the following to adjust the grid orientation.    #
        # The function are flipud and fliplr from Numpy library. See the following links for #
        # more details.                                                                      #
        # https://numpy.org/doc/stable/reference/generated/numpy.flipud.html                 #
        # https://numpy.org/doc/stable/reference/generated/numpy.fliplr.html                 #
        ######################################################################################
        # if dm in ['d02']:
        #     temp[0,90,:,:] = np.flipud(np.fliplr(dfG['PAF'].to_numpy().reshape(shp)))     # Plan area fraction
        #     temp[0,91,:,:] = np.flipud(np.fliplr(dfG['HGT'].to_numpy().reshape(shp)))     # Mean Building Height
        #     temp[0,92,:,:] = np.flipud(np.fliplr(dfG['STD'].to_numpy().reshape(shp)))     # Standard Deviation of Building Height
        #     temp[0,93,:,:] = np.flipud(np.fliplr(dfG['WMBH'].to_numpy().reshape(shp)))    # Area Weighted Mean Building Height
        #     temp[0,94,:,:] = np.flipud(np.fliplr(dfG['BStPA'].to_numpy().reshape(shp)))   # Building Surface to Plan Area Ratio
        #     temp[0,95,:,:] = np.flipud(np.fliplr(dfG['f0'].to_numpy().reshape(shp)))      # Frontal Area Index (Wind Direction=0)
        #     temp[0,96,:,:] = np.flipud(np.fliplr(dfG['f45'].to_numpy().reshape(shp)))     # Frontal Area Index (Wind Direction=45)
        #     temp[0,97,:,:] = np.flipud(np.fliplr(dfG['f90'].to_numpy().reshape(shp)))     # Frontal Area Index (Wind Direction=90)
        #     temp[0,98,:,:] = np.flipud(np.fliplr(dfG['f135'].to_numpy().reshape(shp)))    # Frontal Area Index (Wind Direction=135)
        #     temp[0,99,:,:] = np.flipud(np.fliplr(dfG['CAR'].to_numpy().reshape(shp)))     # Complete Aspect Ratio
        #     for id_ in range(15):
        #         temp[0,117+id_,:,:] = np.flipud(np.fliplr(dfG[f'B_H_{id_}'].to_numpy().reshape(shp)))  # Building Height Histogram
        #         temp[0,id_,:,:]     = np.flipud(np.fliplr(dfG[f'f0_{id_}'].to_numpy().reshape(shp)))   # Frontal area density (Wind Direction=0)
        #         temp[0,15+id_,:,:]  = np.flipud(np.fliplr(dfG[f'f135_{id_}'].to_numpy().reshape(shp))) # Frontal area density (Wind Direction=135)
        #         temp[0,30+id_,:,:]  = np.flipud(np.fliplr(dfG[f'f45_{id_}'].to_numpy().reshape(shp)))  # Frontal area density (Wind Direction=45)
        #         temp[0,45+id_,:,:]  = np.flipud(np.fliplr(dfG[f'f90_{id_}'].to_numpy().reshape(shp)))  # Frontal area density (Wind Direction=90)
        #         temp[0,60+id_,:,:]  = np.flipud(np.fliplr(dfG[f'PAD_{id_}'].to_numpy().reshape(shp)))  # Plan Area Density
        #         temp[0,75+id_,:,:]  = np.flipud(np.fliplr(dfG[f'PAD_{id_}'].to_numpy().reshape(shp)))  # Roof Area Density

        
        mask = temp == 0
        temp[mask] = urb_temp[mask]

        nc['URB_PARAM'][:] = temp[:]
        nc.close()

def gridsize(dm: str) -> int:
    if dm in ['d03', 'd04']: return 1000 * 1000
    if dm == 'd02': return 3000 * 3000
    if dm == 'd01': return 9000 * 9000

def transform():
    df = gpd.read_file('./INT/Home_BC.shp')
    print('done ....... 1')
    df['HGT'] = df['heightmax']
    print('done ....... 2')
    # calculating the frontal area index
    bound_0  = df.bounds
    print('done ....... 3')
    bound_45 = df.rotate(45, use_radians=False).bounds
    print('done ....... 4')
    df['f0']   = np.abs(bound_0['maxx']  - bound_0['minx'])  * df['HGT']
    df['f90']  = np.abs(bound_0['maxy']  - bound_0['miny'])  * df['HGT']
    df['f45']  = np.abs(bound_45['maxx'] - bound_45['minx']) * df['HGT']
    df['f135'] = np.abs(bound_45['maxy'] - bound_45['miny']) * df['HGT']
    print('done ....... 5')
    # calculating Building Surface
    df['Surf'] = df['geometry'].length * df['HGT']
    print('done ....... 6')
    out = gpd.GeoDataFrame(df[['HGT', 'f0', 'f45', 'f90', 'f135', 'bldgarea', 'Surf']], geometry=gpd.points_from_xy(df.centroid.x, df.centroid.y), crs=df.crs)
    return out

def intersct(dm, homes=None, domain=None):
    if homes.crs != domain.crs: domain = domain.to_crs(homes.crs)
    out = gpd.sjoin(homes, domain, how='inner', predicate='intersects')
    out = out.rename(columns={'index_right':'FID_geo_em'})
    return out

if __name__ == '__main__':
    main()