import os
import datetime as dt
import netCDF4
from osgeo import gdal, osr, ogr, gdalconst

from pyramids.raster import Raster

def Convert_nc_to_tiff(input_nc, output_folder):
    """
    This function converts the nc file into tiff files

    Keyword Arguments:
    input_nc -- name, name of the adf file
    output_folder -- Name of the output tiff file
    """

    # All_Data = Raster.Open_nc_array(input_nc)

    if type(input_nc) == str:
        nc = netCDF4.Dataset(input_nc)
    elif type(input_nc) == list:
        nc = netCDF4.MFDataset(input_nc)

    Var = nc.variables.keys()[-1]
    All_Data = nc[Var]

    geo_out, epsg, size_X, size_Y, size_Z, Time = Raster.Open_nc_info(input_nc)

    if epsg == 4326:
        epsg = "WGS84"

    # Create output folder if needed
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    for i in range(0, size_Z):
        if not Time == -9999:
            time_one = Time[i]
            d = dt.fromordinal(time_one)
            name = os.path.splitext(os.path.basename(input_nc))[0]
            nameparts = name.split("_")[0:-2]
            name_out = os.path.join(
                output_folder,
                "_".join(nameparts)
                + "_%d.%02d.%02d.tif" % (d.year, d.month, d.day),
            )
            Data_one = All_Data[i, :, :]
        else:
            name = os.path.splitext(os.path.basename(input_nc))[0]
            name_out = os.path.join(output_folder, name + ".tif")
            Data_one = All_Data[:, :]

        Raster.createRaster(name_out, Data_one, geo_out, epsg)

    return ()


def Convert_grb2_to_nc(input_wgrib, output_nc, band):

    # Get environmental variable
    qgis_path = os.environ["qgis"].split(";")
    GDAL_env_path = qgis_path[0]
    GDAL_TRANSLATE_PATH = os.path.join(GDAL_env_path, "gdal_translate.exe")

    # Create command
    fullCmd = " ".join(
        [
            '"%s" -of netcdf -b %d' % (GDAL_TRANSLATE_PATH, band),
            input_wgrib,
            output_nc,
        ]
    )  # -r {nearest}

    Raster.Run_command_window(fullCmd)

    return ()


def Convert_adf_to_tiff(input_adf, output_tiff):
    """
    This function converts the adf files into tiff files

    Keyword Arguments:
    input_adf -- name, name of the adf file
    output_tiff -- Name of the output tiff file
    """

    # Get environmental variable
    qgis_path = os.environ["qgis"].split(";")
    GDAL_env_path = qgis_path[0]
    GDAL_TRANSLATE_PATH = os.path.join(GDAL_env_path, "gdal_translate.exe")

    # convert data from ESRI GRID to GeoTIFF
    fullCmd = (
                  '"%s" -co COMPRESS=DEFLATE -co PREDICTOR=1 -co ' "ZLEVEL=1 -of GTiff %s %s"
              ) % (GDAL_TRANSLATE_PATH, input_adf, output_tiff)

    Raster.Run_command_window(fullCmd)

    return output_tiff


def Convert_bil_to_tiff(input_bil, output_tiff):
    """
    This function converts the bil files into tiff files

    Keyword Arguments:
    input_bil -- name, name of the bil file
    output_tiff -- Name of the output tiff file
    """

    gdal.GetDriverByName("EHdr").Register()
    dest = gdal.Open(input_bil, gdalconst.GA_ReadOnly)
    Array = dest.GetRasterBand(1).ReadAsArray()
    geo_out = dest.GetGeoTransform()
    Raster.createRaster(output_tiff, Array, geo_out, "WGS84")

    return output_tiff


def Convert_hdf5_to_tiff(
        inputname_hdf, Filename_tiff_end, Band_number, scaling_factor, geo_out
):
    """
    This function converts the hdf5 files into tiff files

    Keyword Arguments:
    input_adf -- name, name of the adf file
    output_tiff -- Name of the output tiff file
    Band_number -- bandnumber of the hdf5 that needs to be converted
    scaling_factor -- factor multipied by data is the output array
    geo -- [minimum lon, pixelsize, rotation, maximum lat, rotation,
            pixelsize], (geospatial dataset)
    """

    # Open the hdf file
    g = gdal.Open(inputname_hdf, gdal.GA_ReadOnly)

    #  Define temporary file out and band name in
    name_in = g.GetSubDatasets()[Band_number][0]

    # Get environmental variable
    qgis_path = os.environ["qgis"].split(";")
    GDAL_env_path = qgis_path[0]
    GDAL_TRANSLATE = os.path.join(GDAL_env_path, "gdal_translate.exe")

    # run gdal translate command
    FullCmd = "%s -of GTiff %s %s" % (GDAL_TRANSLATE, name_in, Filename_tiff_end)
    Raster.Run_command_window(FullCmd)

    # Get the data array
    dest = gdal.Open(Filename_tiff_end)
    Data = dest.GetRasterBand(1).ReadAsArray()
    dest = None

    # If the band data is not SM change the DN values into PROBA-V values and write into the spectral_reflectance_PROBAV
    Data_scaled = Data * scaling_factor

    # Save the PROBA-V as a tif file
    Raster.createRaster(Filename_tiff_end, Data_scaled, geo_out, "WGS84")

    return ()


def Vector_to_Raster(Dir, shapefile_name, reference_raster_data_name):
    """
    This function creates a raster of a shp file

    Keyword arguments:
    Dir --
        str: path to the basin folder
    shapefile_name -- 'C:/....../.shp'
        str: Path from the shape file
    reference_raster_data_name -- 'C:/....../.tif'
        str: Path to an example tiff file (all arrays will be reprojected to this example)
    """
    geo, proj, size_X, size_Y = Raster.openArrayInfo(reference_raster_data_name)

    x_min = geo[0]
    x_max = geo[0] + size_X * geo[1]
    y_min = geo[3] + size_Y * geo[5]
    y_max = geo[3]
    pixel_size = geo[1]

    # Filename of the raster Tiff that will be created
    Dir_Basin_Shape = os.path.join(Dir, "Basin")
    if not os.path.exists(Dir_Basin_Shape):
        os.mkdir(Dir_Basin_Shape)

    Basename = os.path.basename(shapefile_name)
    Dir_Raster_end = os.path.join(
        Dir_Basin_Shape, os.path.splitext(Basename)[0] + ".tif"
    )

    # Open the data source and read in the extent
    source_ds = ogr.Open(shapefile_name)
    source_layer = source_ds.GetLayer()

    # Create the destination data source
    x_res = int(round((x_max - x_min) / pixel_size))
    y_res = int(round((y_max - y_min) / pixel_size))

    # Create tiff file
    target_ds = gdal.GetDriverByName("GTiff").Create(
        Dir_Raster_end, x_res, y_res, 1, gdal.GDT_Float32, ["COMPRESS=LZW"]
    )
    target_ds.SetGeoTransform(geo)
    srse = osr.SpatialReference()
    srse.SetWellKnownGeogCS(proj)
    target_ds.SetProjection(srse.ExportToWkt())
    band = target_ds.GetRasterBand(1)
    target_ds.GetRasterBand(1).SetNoDataValue(-9999)
    band.Fill(-9999)

    # Rasterize the shape and save it as band in tiff file
    gdal.RasterizeLayer(
        target_ds, [1], source_layer, None, None, [1], ["ALL_TOUCHED=TRUE"]
    )
    target_ds = None

    # Open array
    Raster_Basin = Raster.getRasterData(Dir_Raster_end)

    return Raster_Basin