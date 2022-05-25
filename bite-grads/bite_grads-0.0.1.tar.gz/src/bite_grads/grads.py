# -*- coding: utf-8 -*-
"""


@Time    : 2020/9/20 9:52
@Author  : modabao
"""

from datetime import datetime
import re
import sys

import numpy as np
import pandas as pd
import dask.array as daa
import xarray as xr
from pyproj import CRS, Transformer

from bite_grads.ctl import CTL
from bite_grads.tools import parse_wrf_global_comment


class GrADS(object):
    def __init__(self, ctl_path):
        ctl = CTL(ctl_path)
        self.ctl = ctl
        self.fill_value = ctl.undef
        self.coords, shape = get_coords_shape(ctl)
        self.shape = shape
        self.vars = get_vars(ctl, *shape[-2:])
        self.batch_bytes = self.vars['bytes'].sum()
        self.is_wrf = ctl.title.lower().startswith('output from wrf')
        self.dat_path = None
        self.__dtype = None
        self.__proj_dict = {}
        self.__crs = None
        self.__global_attrs = None
        self.__var_attrs = None

    @property
    def dtype(self):
        if (dtype_ := self.__dtype) is None:
            options = self.ctl.options
            if 'big_endian' in options:
                dtype_ = '>f4'
            elif 'little_endian' in options:
                dtype_ = '<f4'
            elif 'byteswapped' in options:
                dtype_ = '<f4' if sys.byteorder == 'big' else '>f4'
            else:
                dtype_ = '>f4' if sys.byteorder == 'big' else '<f4'
            self.__dtype = dtype_
        return dtype_

    @property
    def proj_dict(self):
        ctl = self.ctl
        if not (proj_dict_ := self.__proj_dict.copy()):
            attrs = self.global_attrs
            if pdef := ctl.pdef:
                if pdef['proj'] == 'lcc':
                    proj_dict_ = {
                        'proj': 'lcc',
                        'lat_1': pdef['Struelat'],
                        'lat_2': pdef['Ntruelat']
                    }
                    if self.is_wrf:
                        proj_dict_['lat_0'] = attrs['MOAD_CEN_LAT']
                        proj_dict_['lon_0'] = attrs['STAND_LON']
                        proj_dict_['R'] = 6370000
                    else:
                        proj_dict_['lat_0'] = 0
                        proj_dict_['lon_0'] = pdef['slon']
                        proj_dict_['R'] = 6371200
                    move_lcc_dict(proj_dict_, pdef)
                else:
                    raise Exception(f'{pdef["proj"]} is not yet supported')
            else:
                proj_dict_ = {'proj': 'longlat', 'R': 6371200}
            self.__proj_dict = proj_dict_
        else:
            if pdef := ctl.pdef:
                if pdef['proj'] == 'lcc':
                    move_lcc_dict(proj_dict_, pdef)
        return proj_dict_

    @property
    def crs(self):
        if (crs_ := self.__crs) is None:
            crs_ = self.__crs = CRS.from_dict(self.proj_dict)
        return crs_

    @property
    def global_attrs(self):
        attrs = self.__global_attrs
        attribute_metadata = self.ctl.attribute_metadata
        if attrs is None and not attribute_metadata.empty:
            if self.is_wrf:
                attribute_value = attribute_metadata['attribute_value']
                attrs = attribute_value.apply(parse_wrf_global_comment).set_index('name').squeeze()
            else:
                attrs = attribute_metadata.query('varname == global').set_index('attribute_name')
                attrs = attrs['attribute_value']  # todo: attribute_type
            self.__global_attrs = attrs
        return attrs

    def set_dtype(self, dtype):
        if dtype in ('>f4', '<f4'):
            self.__dtype = dtype
        else:
            raise ValueError('dtype must in {">f4", "<f4"}')

    def set_time(self, time=None, start=None):
        """

        Args:
            time: pd.DatetimeIndex
            start: datetime.datetime

        Returns:
            None

        """
        t: list = list(self.coords['t'])
        if isinstance(time, pd.DatetimeIndex):
            t[1] = time
        elif start:
            t[1] += start - t[1][0]
        self.coords['t'] = tuple(t)

    def set_proj_dict(self, proj_dict):
        crs_ = CRS.from_dict(proj_dict)
        self.__crs = crs_
        self.__proj_dict = proj_dict

    def open_dataset(self, dat_path, need_crs=False, need_global_attrs=False, need_var_attrs=False):
        self.dat_path = dat_path
        size_t = self.shape[0]
        ctl_vars = self.vars
        coords = self.coords
        names = ctl_vars.index
        mask = daa.ma.masked_values
        fill_value = self.fill_value
        data_vars = {
            name: (
                ('t', *ctl_vars.at[name, 'dims']),
                mask(daa.stack([self.read_var_at(name, time_id) for time_id in range(size_t)]), fill_value),
                ({'description': ctl_vars.at[name, 'description']} if need_var_attrs else {}),
                {'coordinates': 'y x'}
            )
            for name in names
        }
        if need_crs:
            crs = self.crs
            crs_cf = crs.to_cf()
            # for panoply recognition
            crs_cf.update({'earth_radius': crs_cf['semi_major_axis']} if crs_cf['inverse_flattening'] == 0 else {})
            coords['crs'] = xr.DataArray(attrs=crs_cf)
            if crs.is_projected:
                for dim in 'xy':
                    coords[dim][2].update({
                        'units': 'm',
                        'long_name': f'{dim} coordinate of projection',
                        'standard_name': f'projection_{dim}_coordinate'
                    })
            else:
                coords['y'][2].update({
                    'units': 'degrees_north',
                    'long_name': 'latitude coordinate',
                    'standard_name': 'latitude'
                })
                coords['x'][2].update({
                    'units': 'degrees_east',
                    'long_name': 'longitude coordinate',
                    'standard_name': 'longitude'
                })
            for name in names:
                data_vars[name][2]['grid_mapping'] = 'crs'
        attrs = self.global_attrs if need_global_attrs else None
        ds = xr.Dataset(data_vars, coords=coords, attrs=attrs)
        return ds

    def read_var_at(self, name, time_id):
        ctl_vars = self.vars
        batch_byte_start = ctl_vars.at[name, 'batch_byte_start']
        offset = time_id * self.batch_bytes + batch_byte_start
        shape = ctl_vars.at[name, 'shape']
        data = np.memmap(self.dat_path, dtype=self.dtype, mode='r', offset=offset, shape=shape)
        return data


def get_t(ctl: CTL):
    tdef = ctl.tdef
    num = tdef['num']
    start = tdef['start']
    increment = tdef['increment']
    match = re.match(r'(?P<hour>\d{2})?:?(?P<minute>\d{2})?z?(?P<day>\d{1,2})?(?P<month>\w{3})(?P<year>\d{2,4})', start)
    hour = match['hour'] or '00'
    minute = match['minute'] or '00'
    day = (match['day'] or '01').zfill(2)
    month = match['month']
    year = match['year']
    year = year if len(year) == 4 else (f'{19 + (year < "50")}' + year)
    start = datetime.strptime(f'{hour}:{minute}Z{day}{month}{year}', '%H:%MZ%d%b%Y')
    unit = 'min' if increment[-2:] == 'mn' else increment[-2].upper()
    increment = increment[:-2] + unit
    if 'template' in ctl.options:
        t = pd.to_datetime([start])
    else:
        t = pd.date_range(start=start, periods=num, freq=increment)
    return t


def get_xy(ctl: CTL):
    if (pdef := ctl.pdef) is None:
        x, y = [
            np.arange(xydef['num'], dtype=np.float32) * xydef['increment'] + xydef['start']
            if (xy := xydef.get('values')) is None else xy for xydef in [ctl.xdef, ctl.ydef]
        ]
    else:
        x = np.arange(pdef['isize']) * pdef['dx']
        y = np.arange(pdef['jsize']) * pdef['dy']
    return x, y


def get_z(ctl: CTL):
    zdef = ctl.zdef
    if (z := zdef.get('values')) is None:
        z = np.arange(zdef['num'], dtype=np.float32) * zdef['increment'] + zdef['start']
    return z


def get_coords_shape(ctl: CTL):
    t = get_t(ctl)
    z = get_z(ctl)
    x, y = get_xy(ctl)
    coords = {
        't': ('t', t, {}),
        'z': ('z', z, {'units': 'hPa'}),
        'y': ('y', y, {}),
        'x': ('x', x, {})
    }
    shape = [len(dim) for dim in [t, z, y, x]]
    return coords, shape


def get_vars(ctl: CTL, size_y: int, size_x: int):
    ctl_vars = ctl.vars
    var_levs = ctl_vars['levs'].values
    bytes_ = var_levs * size_y * size_x * 4
    batch_byte_end = bytes_.cumsum()
    ctl_vars['batch_byte_start'] = np.concatenate([[0], batch_byte_end[:-1]])
    ctl_vars['bytes'] = bytes_
    dims = ('z', 'y', 'x')
    ctl_vars['shape'] = [
        (levs, size_y, size_x) if levs > 1 else (size_y, size_x) for levs in var_levs
    ]
    ctl_vars['dims'] = [
        dims if levs > 1 else dims[1:] for levs in var_levs
    ]
    return ctl_vars


def move_lcc_dict(proj_dict, pdef):
    crs = CRS.from_dict(proj_dict)
    geo2lcc = Transformer.from_crs(crs.geodetic_crs, crs, always_xy=True)
    xref, yref = geo2lcc.transform(pdef['lonref'], pdef['latref'])
    proj_dict['x_0'] = (pdef['iref'] - 1) * pdef['dx'] - xref
    proj_dict['y_0'] = (pdef['jref'] - 1) * pdef['dy'] - yref

