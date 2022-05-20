# -*- coding: utf-8 -*-
"""
Created on Wed Mar 23 22:52:28 2022

@author: zcope
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import ttrs_quicfire.quic_fire as qf
import os
from shapely.geometry import Polygon, Point, LineString, mapping


def boundingbox(shape_paths, buffer, QF_PATH):
    burn_plot = load_shapefile(shape_paths.burn_plot)
    
    #Build bounding box for burn plot
    xmin,ymin,xmax,ymax = burn_plot.loc[[0],'geometry'].total_bounds 
    x_center,y_center = [(xmax+xmin)/2.,(ymax+ymin)/2.]
    x_ext,y_ext = np.ceil([(xmax-xmin)/2,(ymax-ymin)/2]) * 2.
    x0,x1,y0,y1 = [x_center-(x_ext/2.+buffer),x_center+(x_ext/2.+buffer),y_center-(y_ext/2.+buffer),y_center+(y_ext/2.+buffer)]
    polygon = Polygon([(x0, y0), (x0, y1), (x1, y1), (x1, y0), (x0, y0)])
    bbox = gpd.GeoDataFrame( {'col1': ['name1']}, geometry=[polygon], crs=5070)
    bbox_path = os.path.join(shape_paths.SHAPE_PATH,'bbox.shp')
    bbox.to_file(bbox_path)
    shape_paths.bbox = bbox_path
    
    X_length = x1-x0
    Y_length = y1-y0
    
    #Build domain class with bbox xextent
    dom = qf.Domain_Params(X_length=X_length, Y_length=Y_length, dx=2, dy=2, dz=1,
                           nz=128, xmin=x0, ymin=y0, x_center=x_center, 
                           y_center=y_center, shape_paths=shape_paths, QF_PATH=QF_PATH)
    
    return dom

def clip_to_bbox(shp_to_clip, bbox):
    #loads shapefile if given a path
    if isinstance(shp_to_clip, str):
        shp_to_clip = load_shapefile(shp_to_clip)
    if isinstance(bbox, str):
        bbox = load_shapefile(bbox)
    clipped_shape = gpd.clip(shp_to_clip, bbox)
    return clipped_shape


def load_shapefile(file_path):
    shapefile = gpd.read_file(file_path)
    return shapefile.to_crs(epsg=5070)

def linestring_to_polygon(gdf):
    #https://stackoverflow.com/questions/2964751/how-to-convert-a-geos-multilinestring-to-polygon
    gdf['geometry'] = [Polygon(mapping(x)['coordinates']) for x in gdf.geometry]
    return gdf

def polygon_to_linestring(gdf):
    #https://shapely.readthedocs.io/en/stable/manual.html#collections-of-polygons
    # geom = [x for x in gdf.geometry]
    # all_coords = mapping(geom[0])['coordinates']
    # lats = [x[1] for x in all_coords]
    # lons = [x[0] for x in all_coords]
    # line_str = LineString(zip(lons, lats))
    # return gpd.GeoDataFrame(index=[0], crs=gdf.crs, geometry=[line_str])
    gdf['geometry'] = [LineString(x.exterior.coords) for x in gdf.geometry]
    return gdf

def build_ig_lines(shape_paths, spacing, wind_dir):
    bbox = load_shapefile(shape_paths.bbox)
    burnplt = load_shapefile(shape_paths.burn_plot)
    # Ensure burn plot is a ploygon
    if isinstance(burnplt.iloc[0]['geometry'], LineString):
        burnplt = linestring_to_polygon(burnplt)

    ## Establish theta: dir of lines across bbox at angle theta ccw from east
    # arith_dir = arithmatic degree of wind_dir
    if wind_dir > 90 and wind_dir < 360:
        arith_dir = 360 - wind_dir + 90
    elif wind_dir <= 90 and wind_dir >= 0:
        arith_dir = np.negative(wind_dir) + 90


    #theta perpendicur to wind_dir
    theta0 = arith_dir-90
    if theta0 <0:
        theta0 += 360

    # Extent of original bounding box, origin for coord sys @ (xmin,ymin)
    xmin0, ymin0, xmax0, ymax0 = bbox.total_bounds
    # Apply rotation because ignition line code works in the first quadrant
    # i.e. 0 <= theta0 < 90
    if theta0 > 90.0 and theta0 <= 180.0:
        # Rotate bounding box by 90 cw about (xmin0, ymin0)
        bbox = bbox.rotate(-90.0, origin=(xmin0, ymin0))
        theta = theta0 - 90.0
    elif theta0 > 180.0 and theta0 <= 270.0:
        # Rotate bounding box by 180 cw about (xmin0, ymin0)
        bbox = bbox.rotate(-180.0, origin=(xmin0, ymin0))
        theta = theta0 - 180.0
    elif theta0 > 270.0 and theta0 <= 360.0:
        # Rotate bounding box by 270 cw about (xmin0, ymin0)
        bbox = bbox.rotate(-270.0, origin=(xmin0, ymin0))
        theta = theta0 - 270.0
    else:
        theta = theta0
    # Reload the extent of working bounding box (potentially rotated)
    xmin, ymin, xmax, ymax = bbox.total_bounds

    # Line spacing based on number of gridlines (aim to set this directly later)
    rho = int(spacing)
    # Set fine mesh resolution
    nmesh = 128
    # Establish fine mesh on bbox, calibrated to diagonal length
    rmesh = np.sqrt((ymax - ymin) ** 2 + (xmax - xmin) ** 2) / nmesh

    # Algorithm for generating lines on the fine mesh
    # Store all ignition lines in long list
    routes = {}  # Will be a list of GeoDataFrames
    # Iterator through routes
    ii = 0
    # Horizontal (or nearly horizontal) lines do not need the first loop at all
    if np.sin(theta * np.pi / 180.0) > 0.10452846326765346:
        # First loop for drawing lines RIGHT from lower-left corner (xmin, ymin)
        xstart = xmin + (rho / np.sin(theta * np.pi / 180.0))
        # While the starting point lies along the LOWER EDGE of bbox
        while xstart <= xmax:
            # Build line ignition across bbox at angle theta
            xx = xstart
            # Always start these lines along LOWER EDGE of bbox
            yy = ymin
            xline = []  # Will be built up with x-coords
            yline = []  # Will be built up with y-coords
            geom = []  # Stores point geometries (xx, yy)
            # Inner loop to set points along fine mesh
            while (xx <= xmax) and (yy <= ymax):
                # Add x-coords, y-coords, and point geometries to growing list
                xline.append(xx)
                yline.append(yy)
                geom.append(Point(xx, yy))
                # Iterate a distance rmesh across the fine mesh in direction theta
                xx = xx + rmesh * np.cos(theta * np.pi / 180.0)
                yy = yy + rmesh * np.sin(theta * np.pi / 180.0)
            # Build a pandas dataframe with line coordinates
            d = {'col1': np.ones_like(xline), 'col2': xline, 'col3': yline}
            # Print to text file (for diagnostics)
            with open("temp.txt", 'w') as f:
                for key, value in d.items():
                    f.write('%s:%s\n' % (key, value))
            # As long as there is more than one point to work with
            if len(geom) > 1:
                # Draw a LineString
                line = LineString(geom)
                # Build and add this geometry to the routes list
                d = {'geometry': [line]}
                routes[ii] = gpd.GeoDataFrame(d, crs=5070)
                print('...routes[{0}] written to memory'.format(ii))
                # Iterate to next position on routes list
                ii = ii + 1
            # Next line to the RIGHT
            xstart = xstart + (rho / np.sin(theta * np.pi / 180.0))
        # De-iterate (to know where to store lines from the next loop)
        ii = ii - 1
    # Vertial lines do not need the second loop at all
    if np.cos(theta * np.pi / 180.0) != 0.0:
        # Second loop for drawing lines UP from lower-left corner (xmin, ymin)
        ystart = ymin
        # Iterator through routes
        jj = 0
        # While the starting point lies along the LEFT EDGE of bbox
        while ystart <= ymax:
            # Always start along LEFT EDGE of bbox
            xx = xmin
            # Build line ignition across bbox at angle theta
            yy = ystart
            xline = []  # Will be built up with x-coords
            yline = []  # Will be built up with y-coords
            geom = []  # Stores point geometries (xx, yy)
            # Inner loop to set points along fine mesh
            while (xx <= xmax) and (yy <= ymax):
                # Add x-coords, y-coords, and point geometries to growing list
                xline.append(xx)
                yline.append(yy)
                geom.append(Point(xx, yy))
                # Iterate a distance rmesh across the fine mesh in direction theta
                xx = xx + rmesh * np.cos(theta * np.pi / 180.0)
                yy = yy + rmesh * np.sin(theta * np.pi / 180.0)
            # Build a pandas dataframe with line coordinates
            d = {'col1': np.ones_like(xline), 'col2': xline, 'col3': yline}
            # Print to text file (for diagnostics)
            with open("temp.txt", 'w') as f:
                for key, value in d.items():
                    f.write('%s:%s\n' % (key, value))
            # As long as there is more than one point to work with
            if len(geom) > 1:
                # Draw a LineString
                line = LineString(geom)
                # Build and add this geometry to the routes list
                d = {'geometry': [line]}
                routes[ii + jj] = gpd.GeoDataFrame(d, crs=5070)
                print('...routes[{0}] written to memory'.format(ii + jj))
                # Iterate to next position on routes list
                jj = jj + 1
            # Next line UP
            ystart = ystart + (rho / np.cos(theta * np.pi / 180.0))
    # Report size of routes to the user (for diagnostics)
    print('__sizeof__ routes is {0}'.format(routes.__sizeof__()))

    # Apply the opposite rotation as was initially applied to the original bounding box
    routes0 = {}
    if theta0 > 90.0 and theta0 <= 180.0:
        # Loop through routes
        for kk in range(len(routes)):
            # Rotate the ignition lines back to the original frame
            routes0[kk] = routes[kk].rotate(90.0, origin=(xmin0, ymin0))
    elif theta0 > 180.0 and theta0 <= 270.0:
        # Loop through routes
        for kk in range(len(routes)):
            # Rotate the ignition lines back to the original frame
            routes0[kk] = routes[kk].rotate(180.0, origin=(xmin0, ymin0))
    elif theta0 > 270.0 and theta0 <= 360.0:
        # Loop through routes
        for kk in range(len(routes)):
            # Rotate the ignition lines back to the original frame
            routes0[kk] = routes[kk].rotate(-90.0, origin=(xmin0, ymin0))
    else:
        # Loop through routes
        for kk in range(len(routes)):
            # No rotation necessary
            routes0[kk] = routes[kk]

    # Clip routes to the burn plot
    routes0_clip = {}
    for kk in range(len(routes0)):
        routes0_clip[kk] = gpd.clip(routes0[kk], burnplt)

    # Reorganize into a singleton dictionary
    # This is the proper organization to write to shapefile
    Lines = {'geometry': []}
    for kk in range(len(routes0)):
        Lines['geometry'].append(list(routes0[kk].geometry))
    Lines['geometry'] = [val for sublist in Lines['geometry'] for val in sublist]
    ignition = pd.DataFrame(Lines)
    ignition = gpd.GeoDataFrame(ignition, geometry=ignition.geometry, crs=5070)
    
    #Number lines by distance to downwind corner of bbox
    if wind_dir >= 0.0 and wind_dir < 90:
        down_wind_corner = Point(xmin0,ymin0)
    elif wind_dir >= 90.0 and wind_dir < 180.0:
        down_wind_corner = Point(xmin0,ymax0)
    elif wind_dir >= 180.0 and wind_dir < 270.0:
        down_wind_corner = Point(xmax0,ymax0)
    else:
        down_wind_corner = Point(xmax0,ymin0)
    
    #Use distance to down wind corner for sorting ignitions
    ignition['Dist'] = ignition['geometry'].apply(lambda x: x.distance(down_wind_corner))
    #Clip ignition to burnplot
    ignition = gpd.clip(ignition, burnplt)
    #Remove ignitions within 6m of roads
    burnplt_linestring = polygon_to_linestring(burnplt)
    buffered_burnplt_linestring = burnplt_linestring.buffer(6)
    if isinstance(buffered_burnplt_linestring, gpd.geoseries.GeoSeries):
        buffered_burnplt_linestring = gpd.GeoDataFrame(geometry=gpd.GeoSeries(buffered_burnplt_linestring))
    #ignition.to_file(os.path.join(shape_paths.SHAPE_PATH, 'ig_lines_before.shp'))
    ignition = gpd.overlay(ignition, buffered_burnplt_linestring, how = 'difference')
    ignition['Length'] = ignition.geometry.length
    #ignition.to_file(os.path.join(shape_paths.SHAPE_PATH, 'ig_lines_after.shp'))
    return ignition

def line_to_points_to_df(dom, ignition_lines, spacing=4):
    if isinstance(ignition_lines, str):
        ignition_lines = load_shapefile(ignition_lines)
    
    ig_points = gpd.GeoDataFrame()
    for i in range(len(ignition_lines)):
        line = ignition_lines.iloc[i]
        line_geo = line['geometry']
        distance_delta = spacing #Distance in meters
        distances = np.arange(0, line_geo.length, distance_delta)
        points = [line_geo.interpolate(distance) for distance in distances] + [line_geo.boundary[1]]
        temp_dict = {'geometry':points}
        for k in line.keys():
            if k != 'geometry':
                temp_dict[k] = [line[k],]*len(points)        
        temp_points = gpd.GeoDataFrame(temp_dict, crs=5070)
        ig_points = ig_points.append(temp_points)
    #ig_points.to_file(os.path.join(dom.shape_paths.SHAPE_PATH, 'ig_points.shp'))
    
    df = pd.DataFrame(ig_points)
    df['X'] = ig_points.apply(lambda x_dim: (x_dim.geometry.x - dom.xmin), axis=1).to_numpy()
    df['Y'] = ig_points.apply(lambda y_dim: (y_dim.geometry.y - dom.ymin), axis=1).to_numpy()
    df['QF_X_index'] = df['X'].apply(lambda x: int(x/dom.dx)).to_numpy()
    df['QF_Y_index'] = df['Y'].apply(lambda y: int(y/dom.dy)).to_numpy()
    df['IgTime'] = 0.0
    
    return df    