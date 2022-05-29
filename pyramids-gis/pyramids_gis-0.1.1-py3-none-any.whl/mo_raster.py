import sys
import os
import zipfile
import glob
import subprocess
import tarfile
import numpy as np
import datetime as dt
import pandas as pd
import scipy
from pyramids.raster import Raster
from osgeo import gdal, osr
import scipy.misc as misc
# import rasterio.mask
# import rasterio.merge
# import scipy.interpolate
from pyproj import Proj, transform

# import skimage.transform as transform


# TODO: merge with ReprojectDataset and ProjectRaster
def reproject_dataset_epsg(dataset, pixel_spacing, epsg_to, method=2):
    """
    A sample function to reproject and resample a GDAL dataset from within
    Python. The idea here is to reproject from one system to another, as well
    as to change the pixel size. The procedure is slightly long-winded, but
    goes like this:

    1. Set up the two Spatial Reference systems.
    2. Open the original dataset, and get the geotransform
    3. Calculate bounds of new geotransform by projecting the UL corners
    4. Calculate the number of pixels with the new projection & spacing
    5. Create an in-memory raster dataset
    6. Perform the projection

    Keywords arguments:
    dataset -- 'C:/file/to/path/file.tif'
        string that defines the input tiff file
    pixel_spacing -- float
        Defines the pixel size of the output file
    epsg_to -- integer
         The EPSG code of the output dataset
    method -- 1,2,3,4 default = 2
        1 = Nearest Neighbour, 2 = Bilinear, 3 = lanzcos, 4 = average
    """

    # 1) Open the dataset
    g = gdal.Open(dataset)
    if g is None:
        print("input folder does not exist")

    # Get EPSG code
    epsg_from = Raster.getEPSG(g)

    # Get the Geotransform vector:
    geo_t = g.GetGeoTransform()
    # Vector components:
    # 0- The Upper Left easting coordinate (i.e., horizontal)
    # 1- The E-W pixel spacing
    # 2- The rotation (0 degrees if image is "North Up")
    # 3- The Upper left northing coordinate (i.e., vertical)
    # 4- The rotation (0 degrees)
    # 5- The N-S pixel spacing, negative as it is counted from the UL corner
    x_size = g.RasterXSize  # Raster xsize
    y_size = g.RasterYSize  # Raster ysize

    epsg_to = int(epsg_to)

    # 2) Define the UK OSNG, see <http://spatialreference.org/ref/epsg/27700/>
    osng = osr.SpatialReference()
    osng.ImportFromEPSG(epsg_to)
    wgs84 = osr.SpatialReference()
    wgs84.ImportFromEPSG(epsg_from)

    inProj = Proj(init="epsg:%d" % epsg_from)
    outProj = Proj(init="epsg:%d" % epsg_to)

    # Up to here, all  the projection have been defined, as well as a
    # transformation from the from to the to
    ulx, uly = transform(inProj, outProj, geo_t[0], geo_t[3])
    lrx, lry = transform(
        inProj, outProj, geo_t[0] + geo_t[1] * x_size, geo_t[3] + geo_t[5] * y_size
    )

    # See how using 27700 and WGS84 introduces a z-value!
    # Now, we create an in-memory raster
    mem_drv = gdal.GetDriverByName("MEM")

    # The size of the raster is given the new projection and pixel spacing
    # Using the values we calculated above. Also, setting it to store one band
    # and to use Float32 data type.
    col = int((lrx - ulx) / pixel_spacing)
    rows = int((uly - lry) / pixel_spacing)

    # Re-define lr coordinates based on whole number or rows and columns
    (lrx, lry) = (ulx + col * pixel_spacing, uly - rows * pixel_spacing)

    dest = mem_drv.Create("", col, rows, 1, gdal.GDT_Float32)
    if dest is None:
        print("input folder to large for memory, clip input map")

    # Calculate the new geotransform
    new_geo = (ulx, pixel_spacing, geo_t[2], uly, geo_t[4], -pixel_spacing)

    # Set the geotransform
    dest.SetGeoTransform(new_geo)
    dest.SetProjection(osng.ExportToWkt())

    # Perform the projection/resampling
    if method == 1:
        gdal.ReprojectImage(
            g,
            dest,
            wgs84.ExportToWkt(),
            osng.ExportToWkt(),
            gdal.GRA_NearestNeighbour,
        )
    if method == 2:
        gdal.ReprojectImage(
            g, dest, wgs84.ExportToWkt(), osng.ExportToWkt(), gdal.GRA_Bilinear
        )
    if method == 3:
        gdal.ReprojectImage(
            g, dest, wgs84.ExportToWkt(), osng.ExportToWkt(), gdal.GRA_Lanczos
        )
    if method == 4:
        gdal.ReprojectImage(
            g, dest, wgs84.ExportToWkt(), osng.ExportToWkt(), gdal.GRA_Average
        )
    return dest, ulx, lry, lrx, uly, epsg_to


# TODO: merge with ReprojectDataset and ProjectRaster
def reproject_dataset_example(dataset, dataset_example, method=1):
    """
    A sample function to reproject and resample a GDAL dataset from within
    Python. The user can define the wanted projection and shape by defining an example dataset.

    Keywords arguments:
    dataset -- 'C:/file/to/path/file.tif' or a gdal file (gdal.Open(filename))
        string that defines the input tiff file or gdal file
    dataset_example -- 'C:/file/to/path/file.tif' or a gdal file (gdal.Open(filename))
        string that defines the input tiff file or gdal file
    method -- 1,2,3,4 default = 1
        1 = Nearest Neighbour, 2 = Bilinear, 3 = lanzcos, 4 = average
    """
    # open dataset that must be transformed
    try:
        if os.path.splitext(dataset)[-1] == ".tif":
            g = gdal.Open(dataset)
        else:
            g = dataset
    except:
        g = dataset
    epsg_from = Raster.getEPSG(g)

    # exceptions
    if epsg_from == 9001:
        epsg_from = 5070

    # open dataset that is used for transforming the dataset
    try:
        if os.path.splitext(dataset_example)[-1] == ".tif":
            gland = gdal.Open(dataset_example)
            epsg_to = Raster.getEPSG(gland)
        elif os.path.splitext(dataset_example)[-1] == ".nc":

            geo_out, epsg_to, size_X, size_Y, size_Z, Time = Raster.Open_nc_info(
                dataset_example
            )
            data = np.zeros([size_Y, size_X])
            gland = Raster.createRaster(data, geo_out, str(epsg_to))
        else:
            gland = dataset_example
            epsg_to = Raster.getEPSG(gland)
    except:
        gland = dataset_example
        epsg_to = Raster.getEPSG(gland)

    # Set the EPSG codes
    osng = osr.SpatialReference()
    osng.ImportFromEPSG(epsg_to)
    wgs84 = osr.SpatialReference()
    wgs84.ImportFromEPSG(epsg_from)

    # Get shape and geo transform from example
    geo_land = gland.GetGeoTransform()
    col = gland.RasterXSize
    rows = gland.RasterYSize

    # Create new raster
    mem_drv = gdal.GetDriverByName("MEM")
    dest1 = mem_drv.Create("", col, rows, 1, gdal.GDT_Float32)
    dest1.SetGeoTransform(geo_land)
    dest1.SetProjection(osng.ExportToWkt())

    # Perform the projection/resampling
    if method == 1:
        gdal.ReprojectImage(
            g,
            dest1,
            wgs84.ExportToWkt(),
            osng.ExportToWkt(),
            gdal.GRA_NearestNeighbour,
        )
    if method == 2:
        gdal.ReprojectImage(
            g, dest1, wgs84.ExportToWkt(), osng.ExportToWkt(), gdal.GRA_Bilinear
        )
    if method == 3:
        gdal.ReprojectImage(
            g, dest1, wgs84.ExportToWkt(), osng.ExportToWkt(), gdal.GRA_Lanczos
        )
    if method == 4:
        gdal.ReprojectImage(
            g, dest1, wgs84.ExportToWkt(), osng.ExportToWkt(), gdal.GRA_Average
        )
    return dest1


@staticmethod
def MatchNoDataValueArr(arr, src=None, no_val=None):
    """MatchNoDataValueArr.

    MatchNoDataValueArr matchs the nodatavalue from a given src raster/mask array to a an array,
    both the array and the raster has to have the same dimensions.

    Inputs:
    -------
        1-var : [array]
            arr with values to be masked/replaced with the nodata value of
            another raster.
        2-src : [gdal_dataset]
            Instance of the gdal raster to be used to crop/clip the array. src
            overrides the mask and no_val.
        3-mask : [nd_array]
            array with the no_val data
        4-no_val : [float]
            value to be defined as no_val. Will mask anything is not this value

    Outputs:
    --------
        1-var : [nd_array]
            Array with masked values
    """
    assert isinstance(arr, np.ndarray), " first parameter have to be numpy array "

    if isinstance(src, gdal.Dataset) :
        # assert isinstance(src, gdal.Dataset), " src keyword parameter have to be of type gdal.Dataset "
        src, no_val = Raster.GetRasterData(src)
    elif isinstance(src, np.ndarray):
        # src is None
        msg = " You have to enter the value of the no_val parameter when the src is a numpy array"
        assert no_val is not None, msg
    else:
        assert False, "the second parameter 'src' has to be either gdal.Dataset or numpy array"

    # Replace the no_data value
    assert arr.shape == src.shape, 'arc and arr do not have the same shape'

    arr[np.isclose(src, no_val, rtol=0.001)] = no_val
    # for i in range(arr.shape[0]):
    #     for j in range(arr.shape[1]):
    #         if np.isclose(src[i, j], no_val, rtol=0.001):
    #             arr[i, j] = no_val

    return arr

def Extract_Data(input_file, output_folder):
        """
        This function extract the zip files

        Keyword Arguments:
        output_file -- name, name of the file that must be unzipped
        output_folder -- Dir, directory where the unzipped data must be
                               stored
        """
        # extract the data
        z = zipfile.ZipFile(input_file, 'r')
        z.extractall(output_folder)
        z.close()




def Extract_Data_tar_gz(zip_filename, output_folder):
    """
    This function extract the tar.gz files

    Keyword Arguments:
    zip_filename -- name, name of the file that must be unzipped
    output_folder -- Dir, directory where the unzipped data must be
                           stored
    """

    os.chdir(output_folder)
    tar = tarfile.open(zip_filename, "r:gz")
    tar.extractall()
    tar.close()



def Convert_dict_to_array(River_dict, Array_dict, Reference_data):

    if os.path.splitext(Reference_data)[-1] == ".nc":
        # Get raster information
        geo_out, proj, size_X, size_Y, size_Z, Time = Raster.Open_nc_info(
            Reference_data
        )
    else:
        # Get raster information
        geo_out, proj, size_X, size_Y = Raster.openArrayInfo(Reference_data)

    # Create ID Matrix
    y, x = np.indices((size_Y, size_X))
    ID_Matrix = (
            np.int32(
                np.ravel_multi_index(
                    np.vstack((y.ravel(), x.ravel())), (size_Y, size_X), mode="clip"
                ).reshape(x.shape)
            )
            + 1
    )

    # Get tiff array time dimension:
    time_dimension = int(np.shape(Array_dict[0])[0])

    # create an empty array
    DataCube = np.ones([time_dimension, size_Y, size_X]) * np.nan

    for river_part in range(0, len(River_dict)):
        for river_pixel in range(1, len(River_dict[river_part])):
            river_pixel_ID = River_dict[river_part][river_pixel]
            if len(np.argwhere(ID_Matrix == river_pixel_ID)) > 0:
                row, col = np.argwhere(ID_Matrix == river_pixel_ID)[0][:]
                DataCube[:, row, col] = Array_dict[river_part][:, river_pixel]

    return DataCube



def Run_command_window(argument):
    """
    This function runs the argument in the command window without showing cmd window

    Keyword Arguments:
    argument -- string, name of the adf file
    """
    if os.name == 'posix':
        argument = argument.replace(".exe","")
        os.system(argument)

    else:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        process = subprocess.Popen(argument, startupinfo=startupinfo, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        process.wait()

    return()


def Open_bil_array(bil_filename, band=1):
    """
    Opening a bil array.

    Keyword Arguments:
    bil_filename -- 'C:/file/to/path/file.bil'
        string that defines the input tiff file or gdal file
    band -- integer
        Defines the band of the tiff that must be opened.
    """
    gdal.GetDriverByName("EHdr").Register()
    img = gdal.Open(bil_filename)
    Data = img.GetRasterBand(band).ReadAsArray()

    return Data





def Clip_Dataset_GDAL(input_name, output_name, latlim, lonlim):
    """
    Clip the data to the defined extend of the user (latlim, lonlim) by using the gdal_translate executable of gdal.

    Keyword Arguments:
    input_name -- input data, input directory and filename of the tiff file
    output_name -- output data, output filename of the clipped file
    latlim -- [ymin, ymax]
    lonlim -- [xmin, xmax]
    """
    # Get environmental variable
    qgis_path = os.environ["qgis"].split(";")
    GDAL_env_path = qgis_path[0]
    GDALTRANSLATE_PATH = os.path.join(GDAL_env_path, "gdal_translate.exe")

    # find path to the executable
    fullCmd = " ".join(
        [
            "%s" % (GDALTRANSLATE_PATH),
            "-projwin %s %s %s %s -of GTiff %s %s"
            % (lonlim[0], latlim[1], lonlim[1], latlim[0], input_name, output_name),
        ]
    )
    Raster.Run_command_window(fullCmd)

    return ()


def clip_data(input_file, latlim, lonlim):
    """
    Clip the data to the defined extend of the user (latlim, lonlim) or to the
    extend of the DEM tile

    Keyword Arguments:
    input_file -- output data, output of the clipped dataset
    latlim -- [ymin, ymax]
    lonlim -- [xmin, xmax]
    """
    try:
        if input_file.split(".")[-1] == "tif":
            dest_in = gdal.Open(input_file)
        else:
            dest_in = input_file
    except:
        dest_in = input_file

    # Open Array
    data_in = dest_in.GetRasterBand(1).ReadAsArray()

    # Define the array that must remain
    Geo_in = dest_in.GetGeoTransform()
    Geo_in = list(Geo_in)
    Start_x = np.max([int(np.floor(((lonlim[0]) - Geo_in[0]) / Geo_in[1])), 0])
    End_x = np.min(
        [
            int(np.ceil(((lonlim[1]) - Geo_in[0]) / Geo_in[1])),
            int(dest_in.RasterXSize),
        ]
    )

    Start_y = np.max([int(np.floor((Geo_in[3] - latlim[1]) / -Geo_in[5])), 0])
    End_y = np.min(
        [
            int(np.ceil(((latlim[0]) - Geo_in[3]) / Geo_in[5])),
            int(dest_in.RasterYSize),
        ]
    )

    # Create new GeoTransform
    Geo_in[0] = Geo_in[0] + Start_x * Geo_in[1]
    Geo_in[3] = Geo_in[3] + Start_y * Geo_in[5]
    Geo_out = tuple(Geo_in)

    data = np.zeros([End_y - Start_y, End_x - Start_x])

    data = data_in[Start_y:End_y, Start_x:End_x]
    dest_in = None

    return data, Geo_out


def reproject_MODIS(input_name, epsg_to):
    """
    Reproject the merged data file by using gdalwarp. The input projection must be the MODIS projection.
    The output projection can be defined by the user.

    Keywords arguments:
    input_name -- 'C:/file/to/path/file.tif'
        string that defines the input tiff file
    epsg_to -- integer
        The EPSG code of the output dataset
    """
    # Define the output name
    name_out = "".join(input_name.split(".")[:-1]) + "_reprojected.tif"

    # Get environmental variable
    qgis_path = os.environ["qgis"].split(";")
    GDAL_env_path = qgis_path[0]
    GDALWARP_PATH = os.path.join(GDAL_env_path, "gdalwarp.exe")

    # find path to the executable
    fullCmd = " ".join(
        [
            "%s" % (GDALWARP_PATH),
            '-overwrite -s_srs "+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs"',
            "-t_srs EPSG:%s -of GTiff" % (epsg_to),
            input_name,
            name_out,
        ]
    )
    Raster.Run_command_window(fullCmd)

    return name_out





def resize_array_example(Array_in, Array_example, method=1):
    """
    This function resizes an array so it has the same size as an example array
    The extend of the array must be the same

    Keyword arguments:
    Array_in -- []
        Array: 2D or 3D array
    Array_example -- []
        Array: 2D or 3D array
    method: -- 1 ... 5
        int: Resampling method
    """

    # Create old raster
    Array_out_shape = np.int_(Array_in.shape)
    Array_out_shape[-1] = Array_example.shape[-1]
    Array_out_shape[-2] = Array_example.shape[-2]

    if method == 1:
        interpolation_method = "nearest"
        interpolation_number = 0
    if method == 2:
        interpolation_method = "bicubic"
        interpolation_number = 3
    if method == 3:
        interpolation_method = "bilinear"
        interpolation_number = 1
    if method == 4:
        interpolation_method = "cubic"
    if method == 5:
        interpolation_method = "lanczos"

    if len(Array_out_shape) == 3:
        Array_out = np.zeros(Array_out_shape)

        for i in range(0, Array_out_shape[0]):
            Array_in_slice = Array_in[i, :, :]
            size = tuple(Array_out_shape[1:])

            if sys.version_info[0] == 2:
                Array_out_slice = misc.imresize(
                    np.float_(Array_in_slice),
                    size,
                    interp=interpolation_method,
                    mode="F",
                )
            if sys.version_info[0] == 3:
                import skimage.transform as transform

                Array_out_slice = transform.resize(
                    np.float_(Array_in_slice), size, order=interpolation_number
                )

            Array_out[i, :, :] = Array_out_slice

    elif len(Array_out_shape) == 2:

        size = tuple(Array_out_shape)
        if sys.version_info[0] == 2:
            Array_out = misc.imresize(
                np.float_(Array_in), size, interp=interpolation_method, mode="F"
            )
        if sys.version_info[0] == 3:
            import skimage.transform as transform

            Array_out = transform.resize(
                np.float_(Array_in), size, order=interpolation_number
            )

    else:
        print("only 2D or 3D dimensions are supported")

    return Array_out


def gap_filling(dataset, NoDataValue, method=1):
    """
    This function fills the no data gaps in a numpy array

    Keyword arguments:
    dataset -- 'C:/'  path to the source data (dataset that must be filled)
    NoDataValue -- Value that must be filled
    """

    try:
        if dataset.split(".")[-1] == "tif":
            # Open the numpy array
            data = Raster.getRasterData(dataset)
            Save_as_tiff = 1
        else:
            data = dataset
            Save_as_tiff = 0
    except:
        data = dataset
        Save_as_tiff = 0

    # fill the no data values
    if NoDataValue is np.nan:
        mask = ~(np.isnan(data))
    else:
        mask = ~(data == NoDataValue)
    xx, yy = np.meshgrid(np.arange(data.shape[1]), np.arange(data.shape[0]))
    xym = np.vstack((np.ravel(xx[mask]), np.ravel(yy[mask]))).T
    data0 = np.ravel(data[:, :][mask])

    if method == 1:
        interp0 = scipy.interpolate.NearestNDInterpolator(xym, data0)
        data_end = interp0(np.ravel(xx), np.ravel(yy)).reshape(xx.shape)

    if method == 2:
        interp0 = scipy.interpolate.LinearNDInterpolator(xym, data0)
        data_end = interp0(np.ravel(xx), np.ravel(yy)).reshape(xx.shape)

    if Save_as_tiff == 1:
        EndProduct = dataset[:-4] + "_GF.tif"

        # collect the geoinformation
        geo_out, proj, size_X, size_Y = Raster.openArrayInfo(dataset)

        # Save the filled array as geotiff
        Raster.createRaster(
            name=EndProduct, data=data_end, geo=geo_out, projection=proj
        )

    else:
        EndProduct = data_end

    return EndProduct


def Get3Darray_time_series_monthly(Data_Path, Startdate, Enddate, Example_data = None):
    """
    This function creates a datacube

    Keyword arguments:
    Data_Path -- 'product/monthly'
        str: Path to the dataset
    Startdate -- 'YYYY-mm-dd'
        str: startdate of the 3D array
    Enddate -- 'YYYY-mm-dd'
        str: enddate of the 3D array
    Example_data: -- 'C:/....../.tif'
        str: Path to an example tiff file (all arrays will be reprojected to this example)
    """

    # Get a list of dates that needs to be reprojected
    Dates = pd.date_range(Startdate, Enddate, freq = 'MS')

    # Change Working directory
    os.chdir(Data_Path)
    i = 0

    # Loop over the months
    for Date in Dates:

        # Create the end monthly file name
        End_tiff_file_name = 'monthly_%d.%02d.01.tif' %(Date.year, Date.month)

        # Search for this file in directory
        file_name = glob.glob('*%s' %End_tiff_file_name)

        # Select the first file that is found
        file_name_path = os.path.join(Data_Path, file_name[0])

        # Check if an example file is selected
        if Example_data != None:

            # If it is the first day set the example gland file
            if Date == Dates[0]:

                # Check the format to read general info

                # if Tiff
                if os.path.splitext(Example_data)[-1] == '.tif':
                    geo_out, proj, size_X, size_Y = Raster.openArrayInfo(Example_data)
                    dataTot=np.zeros([len(Dates),size_Y,size_X])

                # if netCDF
                if os.path.splitext(Example_data)[-1] == '.nc':
                    geo_out, projection, size_X, size_Y, size_Z, Time = Raster.Open_nc_info(Example_data)
                    dataTot=np.zeros([len(Dates),size_Y,size_X])

                    # Create memory file for reprojection
                    data = Raster.Open_nc_array(Example_data, "Landuse")
                    driver = gdal.GetDriverByName("MEM")
                    gland = driver.Create('', int(size_X), int(size_Y), 1,
                                           gdal.GDT_Float32)
                    srse = osr.SpatialReference()
                    if projection == '' or projection == 4326:
                        srse.SetWellKnownGeogCS("WGS84")
                    else:
                        srse.SetWellKnownGeogCS(projection)
                    gland.SetProjection(srse.ExportToWkt())
                    gland.GetRasterBand(1).SetNoDataValue(-9999)
                    gland.SetGeoTransform(geo_out)
                    gland.GetRasterBand(1).WriteArray(data)

                # use the input parameter as it is already an example file
                else:
                    gland = Example_data

            # reproject dataset
            dest = Raster.reproject_dataset_example(file_name_path, gland, method = 4)
            Array_one_date = dest.GetRasterBand(1).ReadAsArray()

        # if there is no example dataset defined
        else:

            # Get the properties from the first file
            if Date is Dates[0]:
                    geo_out, proj, size_X, size_Y = Raster.openArrayInfo(file_name_path)
                    dataTot=np.zeros([len(Dates),size_Y,size_X])
            Array_one_date = Raster.GetRasterData(file_name_path)

        # Create the 3D array
        dataTot[i,:,:] = Array_one_date
        i += 1

    return dataTot






def Moving_average(dataset, Moving_front, Moving_back):
    """
    This function applies the moving averages over a 3D matrix called dataset.

    Keyword Arguments:
    dataset -- 3D matrix [time, ysize, xsize]
    Moving_front -- Amount of time steps that must be considered in the front of the current month
    Moving_back -- Amount of time steps that must be considered in the back of the current month
    """

    dataset_out = np.zeros(
        (
            int(np.shape(dataset)[0]) - Moving_back - Moving_front,
            int(np.shape(dataset)[1]),
            int(np.shape(dataset)[2]),
        )
    )

    for i in range(Moving_back, (int(np.shape(dataset)[0]) - Moving_front)):
        dataset_out[i - Moving_back, :, :] = np.nanmean(
            dataset[i - Moving_back: i + 1 + Moving_front, :, :], 0
        )

    return dataset_out



def Get_ordinal(Startdate, Enddate, freq="MS"):
    """
    This function creates an array with ordinal time.

    Keyword Arguments:
    Startdate -- Startdate of the ordinal time
    Enddate -- Enddate of the ordinal time
    freq -- Time frequencies between start and enddate
    """

    Dates = pd.date_range(Startdate, Enddate, freq=freq)
    i = 0
    ordinal = np.zeros([len(Dates)])
    for date in Dates:
        p = dt.date(date.year, date.month, date.day).toordinal()
        ordinal[i] = p
        i += 1

    return ordinal



def Create_Buffer(Data_In, Buffer_area):
   '''
   This function creates a 3D array which is used to apply the moving window
   '''

   # Buffer_area = 2 # A block of 2 times Buffer_area + 1 will be 1 if there is the pixel in the middle is 1
   Data_Out=np.empty((len(Data_In),len(Data_In[1])))
   Data_Out[:,:] = Data_In
   for ypixel in range(0,Buffer_area + 1):

        for xpixel in range(1,Buffer_area + 1):

           if ypixel==0:
                for xpixel in range(1,Buffer_area + 1):
                    Data_Out[:,0:-xpixel] += Data_In[:,xpixel:]
                    Data_Out[:,xpixel:] += Data_In[:,:-xpixel]

                for ypixel in range(1,Buffer_area + 1):

                    Data_Out[ypixel:,:] += Data_In[:-ypixel,:]
                    Data_Out[0:-ypixel,:] += Data_In[ypixel:,:]

           else:
               Data_Out[0:-xpixel,ypixel:] += Data_In[xpixel:,:-ypixel]
               Data_Out[xpixel:,ypixel:] += Data_In[:-xpixel,:-ypixel]
               Data_Out[0:-xpixel,0:-ypixel] += Data_In[xpixel:,ypixel:]
               Data_Out[xpixel:,0:-ypixel] += Data_In[:-xpixel,ypixel:]

   Data_Out[Data_Out>0.1] = 1
   Data_Out[Data_Out<=0.1] = 0

   return Data_Out