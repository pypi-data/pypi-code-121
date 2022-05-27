import os.path
import numpy as np
import pickle
import astropy.units as u
import json
import sqlalchemy as sqla
import sqlalchemy.dialects.postgresql as pg

from nexoclom.math import rotation_matrix, Histogram2d
from nexoclom.modelcode.ModelResult import ModelResult
from nexoclom.modelcode.Output import Output

import bokeh.plotting as bkp
from bokeh.palettes import Inferno256
from bokeh.models import (HoverTool, ColumnDataSource, ColorBar,
                          LogColorMapper, LogTicker, LinearColorMapper)
from bokeh.io import curdoc, export_png
from bokeh.themes import Theme


class ModelImage(ModelResult):
    def __init__(self, inputs, params, filenames=None, overwrite=False):
        """ Create Images from model results.
        This Assumes the model has already been run.
        
        Parameters
        ==========
        inputs
            An Input object
        
        params
            A dictionary with format information or a path to a formatfile.
            
        filenames
            A filename or list of filenames to use. Default = None is to
            find all files created for the inputs.
            
        overwrite
            If True, deletes any images that have already been computed.
            Default = False
        """
        super().__init__(inputs, params)
        self.type = 'image'
        self.origin = self.params.get('origin', inputs.geometry.planet)
        self.unit = u.def_unit('R_' + self.origin.object,
                               self.origin.radius)

        dimtemp = self.params.get('dims', '800,800').split(',')
        self.dims = [int(dimtemp[0]), int(dimtemp[1])]

        centtemp = self.params.get('center', '0,0').split(',')
        self.center = [float(centtemp[0])*self.unit,
                       float(centtemp[1])*self.unit]

        widtemp = self.params.get('width', '8,8').split(',')
        self.width = [float(widtemp[0])*self.unit,
                      float(widtemp[1])*self.unit]

        subobslong = self.params.get('subobslongitude', '0')
        self.subobslongitude = float(subobslong) * u.rad

        subobsllat = self.params.get('subobslatitude', np.pi/2)
        self.subobslatitude = float(subobsllat) * u.rad

        self.image = np.zeros(self.dims)
        self.packet_image = np.zeros(self.dims)
        self.blimits = None
        immin = tuple(c - w/2 for c, w in zip(self.center, self.width))
        immax = tuple(c + w/2 for c, w in zip(self.center, self.width))
        self.xrange = [immin[0], immax[0]]
        self.zrange = [immin[1], immax[1]]
        scale = tuple(w/d for w, d in zip(self.width, self.dims))
        self.Apix = (scale[0]*scale[1]).to(u.cm**2)

        self.xaxis = None
        self.zaxis = None

        self.outid, self.outputfiles, _, _ = self.inputs.search()
        
        for i, fname in enumerate(self.outputfiles):
            # Search to see if its already been done
            print(f'Output filename: {fname}')
            image_, packets_ = self.restore(fname, overwrite=overwrite)
            output = Output.restore(fname)

            if image_ is None:
                image_, packets_, = self.create_image(output)
                print(f'Completed image {i+1} of {len(self.outputfiles)}')
            else:
                print(f'Image {i+1} of {len(self.outputfiles)} '
                       'previously completed.')

            self.image += image_.histogram
            self.packet_image += packets_.histogram
            self.totalsource += output.totalsource
            self.xaxis = image_.x * self.unit
            self.zaxis = image_.y * self.unit
            del output

        mod_rate = self.totalsource / self.inputs.options.endtime.value
        self.atoms_per_packet = 1e23 / mod_rate
        self.sourcerate = 1e23 / u.s
        self.image *= self.atoms_per_packet

    def save(self, fname, image, packets):
        # Determine the id of the outputfile
        engine = self.inputs.config.create_engine()
        metadata_obj = sqla.MetaData()
        outputfile = sqla.Table("outputfile", metadata_obj, autoload_with=engine)

        idnum_query = sqla.select(outputfile.columns.idnum).where(
            outputfile.columns.filename == fname)
        with engine.commnect() as con:
            idnum_= con.execute(idnum_query).first()
        idnum = idnum_.idnum

        # Insert the image into the database
        engine = self.inputs.config.create_engine()
        metadata_obj = sqla.MetaData()
        table = sqla.Table("modelimages", metadata_obj, autoload_with=engine)
        
        insert_stmt = pg.insert(table).values(
            out_idnum = idnum,
            quantity = self.quantity,
            origin = self.origin.object,
            dims = self.dims,
            center = [c.value for c in self.center],
            width = [w.value for w in self.width],
            subobslongitude = self.subobslongitude.value,
            subobslatitude = self.subobslatitude.value,
            mechanism = self.mechanism,
            wavelength = [w.value for w in self.wavelength])

        with engine.connect() as con:
            result = con.execute(insert_stmt)
            con.commit()

        self.idnum = result.inserted_primary_key[0]
        savefile = os.path.join(os.path.dirname(fname), f'image.{self.idnum}.pkl')
        update = sqla.update(table).where(table.columns.idnum == self.idnum).values(
            filename=savefile)
        with engine.connect() as con:
            con.execute(update)
            con.commit()

        with open(savefile, 'wb') as f:
            pickle.dump((image, packets), f)

    def restore(self, fname, overwrite=False):
        # Determine the id of the outputfile
        engine = self.inputs.config.create_engine()
        metadata_obj = sqla.MetaData()
        outputfile = sqla.Table("outputfile", metadata_obj, autoload_with=engine)
        
        idnum_query = sqla.select(outputfile.columns.idnum).where(
            outputfile.columns.filename == fname)
        with engine.commnect() as con:
            idnum_= con.execute(idnum_query).first()
        oid = idnum_.idnum

        images = sqla.Table("modelimages", metadata_obj, autoload_with=engine)
        im_query = sqla.select(images.columns.filename).where(
            images.columns.out_idnum == oid,
            images.columns.quantity == self.quantity,
            images.columns.origin == self.origin.object,
            images.columns.dims == self.dims,
            images.columns.center == [s.value for s in self.center],
            images.columns.width == [w.value for w in self.width],
            images.columns.subobslongitude == self.subobslongitude.value,
            images.columns.subobslatitude == self.subobslatitude.value,
            images.columns.mechanism == self.mechanism,
            images.columns.wavelength == self.wavelength)
        
        with engine.connect() as con:
            result = con.execute(im_query).first()

        if (len(result) == 1) and overwrite:
            delete = sqla.delete(images).where(
                images.columns.filename == result.filename)
            if os.path.exists(result.filename):
                os.remove(result.filename)
            image, packets = None, None
        elif len(result) == 1:
            image, packets = pickle.load(open(result.filename[0], 'rb'))
        elif len(result) == 0:
            image, packets = None, None
        else:
            raise RuntimeError('ModelImage.restore',
                               'Should not be able to get here.')

        return image, packets

    def create_image(self, output):
        # Determine the proper frame rotation
        M = self.image_rotation()

        # Load data in solar reference frame
        packets = output.X
        if self.origin != self.inputs.geometry.planet:
            super().transform_reference_frame(packets)
        
        packets['radvel_sun'] = (packets['vy'] +
                                 output.vrplanet.to(self.unit/u.s).value)

        # packet positions in an array
        pts_sun = packets[['x', 'y', 'z']].values

        # Rotate to observer frame
        pts_obs = np.array(np.matmul(M, pts_sun.transpose()).transpose())

        # Determine which packets are not blocked by planet
        rhosqr_obs = np.linalg.norm(pts_obs[:, [0, 2]], axis=1)
        inview = (rhosqr_obs > 1) | (pts_obs[:,1] < 0)
        packets['frac'] *= inview

        # Which packets are in sunlight
        rhosqr_sun = np.linalg.norm(pts_sun[:, [0, 2]], axis=1)
        out_of_shadow = (rhosqr_sun > 1) | (pts_sun[:,1] < 0)

        # Packet weighting
        self.packet_weighting(packets, out_of_shadow, output.aplanet)
        packets['weight'] /= self.Apix

        pts_obs = pts_obs.transpose()
        range = [[x.value for x in self.xrange],
                 [z.value for z in self.zrange]]
        image = Histogram2d(pts_obs[0,:], pts_obs[2,:], weights=packets['weight'],
                            bins=self.dims, range=range)
        packim = Histogram2d(pts_obs[0,:], pts_obs[2,:], bins=self.dims, range=range)
        self.xaxis = image.x * self.unit
        self.zaxis = image.y * self.unit
        self.save(output.filename, image, packim)

        return image, packim

    def display(self, savefile='image.html', limits=None, show=True, log=True):
        if self.unit.__str__() == 'R_Mercury':
            ustr = 'R_M'
        else:
            ustr = 'R_obj'
            
        if self.quantity == 'radiance':
            runit = 'kR'
            rname = 'Radiance'
        elif self.quantity == 'column':
            runit = 'cm-2'
            rname = 'Column'
        else:
            assert 0

        tooltips = [('x', '$x{0.1f} ' + ustr),
                    ('y', '$y{0.1f} ' + ustr),
                    (rname, '@image ' + runit)]
        
        curdoc().theme = Theme(os.path.join(os.path.dirname(__file__),
                                            'data', 'bokeh.yml'))

        if log:
            if limits is None:
                limits = (self.image[self.image > 0].min(), self.image.max())
            else:
                pass
            color_mapper = LogColorMapper(palette=Inferno256, low=limits[0],
                                          high=limits[1])
        else:
            if limits is None:
                limits = (0, self.image.max())
            else:
                pass
            color_mapper = LinearColorMapper(palette=Inferno256, low=limits[0],
                                             high=limits[1])

        x0 = np.min(self.xaxis.value)
        y0 = np.min(self.zaxis.value)
        dw = np.max(self.xaxis.value) - np.min(self.xaxis.value)
        dh = np.max(self.zaxis.value) - np.min(self.zaxis.value)

        fig = bkp.figure(plot_width=1000, plot_height=1000,
                         title=f'{self.inputs.options.species} {rname}',
                         x_axis_label=f'Distance ({ustr})',
                         y_axis_label=f'Distance ({ustr})',
                         x_range=[np.min(self.xaxis.value),
                                  np.max(self.xaxis.value)],
                         y_range=[np.min(self.zaxis.value),
                                  np.max(self.zaxis.value)],
                         tooltips=tooltips)

        fig.image(image=[self.image.T], x=x0, y=y0, dw=dw, dh=dh,
                  color_mapper=color_mapper)
        xc = np.cos(np.linspace(0, 2*np.pi, 1000))
        yc = np.sin(np.linspace(0, 2*np.pi, 1000))
        fig.patch(xc, yc, fill_color='yellow')
        
        bkp.output_file(savefile)
        export_png(fig, filename=savefile.replace('.html', '.png'))
        if show:
            bkp.show(fig)
        else:
            bkp.save(fig)
            
        #
        # # Determine limits if none given
        # if limits is None:
        #     interval = PercentileInterval(95)
        #     self.blimits = interval.get_limits(self.image[self.image > 0])
        # elif len(limits) == 2:
        #     self.blimits = limits
        # else:
        #     assert 0, 'Problem with the display limits'

#        norm = ImageNormalize(self.image, stretch=LogStretch(),
#                              vmin=self.blimits[0], vmax=self.blimits[1])

        # # Make the colorbar
        # if self.quantity == 'column':
        #     clabel = f'$N_{{ {self.inputs.options.species} }}\ cm^{{-2}}$'
        # else:
        #     clabel = f'$I_{{ {self.inputs.options.species} }} R$'
        # cbar = fig.colorbar(im, shrink=0.7, label=clabel)

        # Put Planet's disk in the middle
        # xc, yc = (np.cos(np.linspace(0, 2*np.pi, 1000)),
        #           np.sin(np.linspace(0, 2*np.pi, 1000)))
        # ax.fill(xc, yc, 'y')

        return fig
    
    def image_rotation(self):
        slong = self.subobslongitude
        slat = self.subobslatitude
        
        pSun = np.array([0., -1., 0.])
        pObs = np.array([np.sin(slong)*np.cos(slat),
                         -np.cos(slong)*np.cos(slat),
                         np.sin(slat)])
        if np.array_equal(pSun, pObs):
            M = np.eye(3)
        else:
            costh = np.dot(pSun, pObs)/np.linalg.norm(pSun)/np.linalg.norm(pObs)
            theta = np.arccos(np.clip(costh, -1, 1))
            axis = np.cross(pSun, pObs)
            M = rotation_matrix(theta, axis)
        
        #M = np.transpose(M)
        return M

    def export(self, filename='image.json'):
        if filename.endswith('.json'):
            saveimage = {'image':self.image.tolist(),
                         'xaxis':self.xaxis.value.tolist(),
                         'zaxis':self.zaxis.value.tolist()}
            with open(filename, 'w') as f:
                json.dump(saveimage, f)
        else:
            raise TypeError('Not an valid file format')
