"""Read the model inputs from a file and create the Input object.

The Input object is build from smaller objects defining different model
options.

Geometry
    Defines the Solar System geometry for the Input.

SurfaceInteraction
    Defines the surface interactions.

Forces
    Set which forces act on model particles.

SpatialDist
    Define the initial spatial distribution of particles.

SpeedDist
    Define the initial speed distribution of particles.

AngularDist
    Define the initial angular distribtuion of particles.

Options
    Configure other model parameters
"""
import os
import os.path
import numpy as np
import pandas as pd
from astropy.time import Time
import sqlalchemy as sqla
from nexoclom.modelcode.Output import Output
from nexoclom.utilities import NexoclomConfig
from nexoclom.modelcode.input_classes import (Geometry, SurfaceInteraction,
                                             Forces, SpatialDist, SpeedDist,
                                             AngularDist, Options)
from nexoclom.modelcode.ModelImage import ModelImage

class Input:
    def __init__(self, infile):
        """Read the input options from a file.

        **Parameters**
        
        infile
            Plain text file containing model input parameters. See
            :doc:`inputfiles` for a description of the input file format.

        **Class Attributes**

        * geometry
        
        * surface_interaction
        
        * forces
        
        * spatialdist
        
        * speeddist
        
        * angulardist
        
        * options
        
        """
        # Read the configuration file
        self.config = NexoclomConfig()
        # self._savepath = NexoclomConfig().savepath

        # Read in the input file:
        self._inputfile = infile
        params = []
        if os.path.isfile(infile):
            # Remove everything in the line after a comment character
            for line in open(infile, 'r'):
                if ';' in line:
                    line = line[:line.find(';')]
                elif '#' in line:
                    line = line[:line.find('#')]
                else:
                    pass
                    
                if line.count('=') == 1:
                    param_, val_ = line.split('=')
                    if param_.count('.') == 1:
                        sec_, par_ = param_.split('.')
                        params.append((sec_.casefold().strip(),
                                       par_.casefold().strip(),
                                       val_.strip()))
                    else:
                        pass
                else:
                    pass
        else:
            raise FileNotFoundError(infile)
            
        def extract_param(tag):
            return {b: c for (a, b, c) in params if a == tag}

        self.geometry = Geometry(extract_param('geometry'))
        self.surfaceinteraction = SurfaceInteraction(extract_param(
            'surfaceinteraction'))
        self.forces = Forces(extract_param('forces'))
        self.spatialdist = SpatialDist(extract_param('spatialdist'))
        self.speeddist = SpeedDist(extract_param('speeddist'))
        self.angulardist = AngularDist(extract_param('angulardist'))
        self.options = Options(extract_param('options'))
        
    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        else:
            return all([self.geometry == other.geometry,
                        self.surfaceinteraction == other.surfaceinteraction,
                        self.forces == other.forces,
                        self.spatialdist == other.spatialdist,
                        self.speeddist == other.speeddist,
                        self.angulardist == other.angulardist,
                        self.options == other.options])
        
    def __repr__(self):
        return self.__str__()

    def __str__(self):
        result = (self.geometry.__str__() + '\n' +
                  self.surfaceinteraction.__str__() + '\n' +
                  self.forces.__str__() + '\n' +
                  self.spatialdist.__str__() + '\n' +
                  self.speeddist.__str__() + '\n' +
                  self.angulardist.__str__() + '\n' +
                  self.options.__str__())
        
        return result

    def search(self):
        """ Search the database for previous model runs with the same inputs.
        See :doc:`searchtolerances` for tolerances used in searches.
        
        **Parameters**
        
        No parameters.
        
        **Returns**
        
        * A list of filenames corresponding to the inputs.
        
        * Number of packets contained in those saved outputs.
        
        * Total modeled source rate.
        """
        geo_id = self.geometry.search()
        sint_id = self.surfaceinteraction.search()
        for_id = self.forces.search()
        spat_id = self.spatialdist.search()
        spd_id = self.speeddist.search()
        ang_id = self.angulardist.search()
        opt_id = self.options.search()
        
        if None in [geo_id, sint_id, for_id, spat_id, spd_id, ang_id, opt_id]:
            return [], [], 0., 0.
        else:
            engine = self.config.create_engine()
            metadata_obj = sqla.MetaData()
            
            table = sqla.Table("outputfile", metadata_obj, autoload_with=engine)
            query = sqla.select(table).where(
                table.columns.geo_type == self.geometry.type,
                table.columns.geo_id == geo_id,
                table.columns.sint_type == self.surfaceinteraction.sticktype,
                table.columns.sint_id == sint_id,
                table.columns.force_id == for_id,
                table.columns.spatdist_type == self.spatialdist.type,
                table.columns.spatdist_id == spat_id,
                table.columns.spddist_type == self.speeddist.type,
                table.columns.spddist_id == spd_id,
                table.columns.angdist_type == self.angulardist.type,
                table.columns.angdist_id == ang_id,
                table.columns.opt_id == opt_id)
            
            with self.config.create_engine().connect() as con:
                result = pd.DataFrame(con.execute(query))
            
            if len(result) > 0:
                return (result.idnum.to_list(), result.filename.to_list(),
                        result.npackets.sum(), result.totalsource.sum())
            else:
                return [], [], 0, 0


    def run(self, npackets, packs_per_it=None, overwrite=False, compress=True):
        """Run the nexoclom model with the current inputs.
        
        **Parameters**
        
        npackets
            Number of packets to simulate
        
        packs_per_it
            Maximum number of packets to run at one time. Default = 1e5 in
            constant step-size mode; 1e6 in adaptive step-size mode.
        
        overwrite
            Erase any files matching the current inputs that exist.
            Default = False
            
        compress
            Remove packets with frac=0 from the outputs to reduce file size.
            Default = True
            
        **Outputs**
        
        Nothing is returned, but model runs are saved and cataloged.
        """
        t0_ = Time.now()
        print(f'Starting at {t0_}')

        # Determine how many packets have already been run
        if overwrite:
            self.delete_files()
            totalpackets = 0
        else:
            _, outputfiles, totalpackets, _ = self.search()
            print(f'Found {len(outputfiles)} files with {totalpackets} '
                  'packets.')

        npackets = int(npackets)
        ntodo = npackets - totalpackets
        
        if ntodo > 0:
            if (packs_per_it is None) and (self.options.step_size == 0):
                packs_per_it = 1000000
            elif packs_per_it is None:
                packs_per_it = (1e8 * self.options.step_size /
                                self.options.endtime.value)
            else:
                pass
            packs_per_it = int(np.min([ntodo, packs_per_it]))
            
            # Determine how many iterations are needed
            nits = int(np.ceil(ntodo/packs_per_it))
            
            print('Running Model')
            print(f'Will complete {nits} iterations of {packs_per_it} packets.')

            for _ in range(nits):
                tit0_ = Time.now()
                print(f'Starting iteration #{_+1} of {nits}')

                # Create an output object
                Output(self, packs_per_it, compress=compress)
                tit1_ = Time.now()
                print(f'Completed iteration #{_+1} in '
                      f'{(tit1_ - tit0_).sec} seconds.')
        else:
            pass

        t2_ = Time.now()
        dt_ = (t2_-t0_).sec
        if dt_ < 60:
            dt_ = f'{dt_} sec'
        elif dt_ < 3600:
            dt_ = f'{dt_/60} min'
        else:
            dt_ = f'{dt_/3600} hr'
        print(f'Model run completed in {dt_} at {t2_}.')

    def produce_image(self, format_, filenames=None, overwrite=False):
        return ModelImage(self, format_, filenames=filenames,
                          overwrite=overwrite)
    
    def delete_files(self):
        """Delete output files and remove them from the database.

        **Parameters**

        filelist
            List of files to remove. This can be found with Inputs.search()

        **Returns**

        No outputs.

        """
        idnum, filelist, _, _ = self.search()
        engine = self.config.create_engine()
        metadata_obj = sqla.MetaData()
        outputfile = sqla.Table("outputfile", metadata_obj, autoload_with=engine)
        modelimages = sqla.Table("modelimages", metadata_obj, autoload_with=engine)
        uvvsmodels = sqla.Table("uvvsmodels", metadata_obj, autoload_with=engine)
        spatdist = sqla.Table("spatdist_fittedoutput", metadata_obj,
                              autoload_with=engine)
        speeddist = sqla.Table("speeddist_fittedoutput", metadata_obj,
                              autoload_with=engine)
        
        for outid, outfile in zip(idnum, filelist):
            # Remove from database and delete file
            out_del = sqla.delete(outputfile).where(
                outputfile.columns.idnum == outid)
            
            # Delete any model images that depend on this output
            mod_select = sqla.select(modelimages).where(
                modelimages.columns.out_idnum == outid)
            mod_del = sqla.delete(modelimages).where(
                modelimages.columns.out_idnum == outid)

            # Delete any uvvs models that depend on this output
            uvvs_select = sqla.select(uvvsmodels).where(
                uvvsmodels.columns.out_idnum == outid)
            uvvs_del = sqla.delete(modelimages).where(
                uvvsmodels.columns.out_idnum == outid)
            
            # Delete any fitted uvvs models that depend on this output
            uvvsfit_select = sqla.select(uvvsmodels).where(
                uvvsmodels.columns.unfit_idnum == outid)
            uvvsfit_del = sqla.delete(modelimages).where(
                uvvsmodels.columns.unfit_idnum == outid)

            # Delete any fitted outputs that depend on this output
            fitted_spat_select = sqla.select(spatdist.columns.idnum).where(
                spatdist.columns.unfit_outid == outid)
            fitted_spat_delete = sqla.delete(spatdist).where(
                spatdist.columns.unfit_outid == outid)
            
            fitted_speed_select = sqla.select(speeddist.columns.idnum).where(
                speeddist.columns.unfit_outid == outid)
            fitted_speed_delete = sqla.delete(speeddist).where(
                speeddist.columns.unfit_outid == outid)
            
            fitted_out_spat_select = sqla.select(outputfile).where(
                outputfile.columns.spatdist_id.in_(fitted_spat_select),
                outputfile.columns.spatdist_type == 'fitted output')
            fitted_out_spat_select_ = sqla.select(outputfile.columns.idnum).where(
                outputfile.columns.spatdist_id.in_(fitted_spat_select),
                outputfile.columns.spatdist_type == 'fitted output')
            fitted_out_spat_delete = sqla.select(outputfile).where(
                outputfile.columns.spatdist_id.in_(fitted_spat_select),
                outputfile.columns.spatdist_type == 'fitted output')
            
            fitted_out_speed_select = sqla.select(outputfile).where(
                outputfile.columns.spddist_id.in_(fitted_speed_select),
                outputfile.columns.spddist_type == 'fitted output')
            fitted_out_speed_select_ = sqla.select(outputfile.columns.idnum).where(
                outputfile.columns.spddist_id.in_(fitted_speed_select),
                outputfile.columns.spddist_type == 'fitted output')
            fitted_out_speed_delete = sqla.select(outputfile).where(
                outputfile.columns.spddist_id.in_(fitted_speed_select),
                outputfile.columns.spddist_type == 'fitted output')
            
            # Delete any model images that depend on the fitted outputs
            fitted_images_spat_select = sqla.select(modelimages).where(
                modelimages.columns.out_idnum.in_(fitted_out_spat_select_))
            fitted_images_spat_delete = sqla.delete(modelimages).where(
                modelimages.columns.out_idnum.in_(fitted_out_spat_select_))

            fitted_images_speed_select = sqla.select(modelimages).where(
                modelimages.columns.out_idnum.in_(fitted_out_speed_select_))
            fitted_images_speed_delete = sqla.delete(modelimages).where(
                modelimages.columns.out_idnum.in_(fitted_out_speed_select_))

            with engine.connect() as con:
                mod_files = con.execute(mod_select)
                uvvs_files = con.execute(uvvs_select)
                uvvs_fit_files = con.execute(uvvsfit_select)
                fitted_out_spat_files = con.execute(fitted_out_spat_select)
                fitted_out_speed_files = con.execute(fitted_out_speed_select)
                fitted_images_spat_files = con.execute(fitted_images_spat_select)
                fitted_images_speed_files = con.execute(fitted_images_speed_select)
                
                con.execute(out_del)
                con.execute(mod_del)
                con.execute(uvvs_del)
                con.execute(uvvsfit_del)
                con.execute(fitted_spat_delete)
                con.execute(fitted_speed_delete)
                con.execute(fitted_out_spat_delete)
                con.execute(fitted_out_speed_delete)
                con.execute(fitted_images_spat_delete)
                con.execute(fitted_images_speed_delete)
                con.commit()
                
            if os.path.exists(outfile):
                print(f'Removing file {outfile}')
                os.remove(outfile)
                
            for row in mod_files:
                if os.path.exists(row.filename):
                    print(f'Removing file {row.filename}')
                    os.remove(row.filename)
                    
            for row in uvvs_files:
                if os.path.exists(row.filename):
                    print(f'Removing file {row.filename}')
                    os.remove(row.filename)
                    
            for row in uvvs_fit_files:
                if os.path.exists(row.filename):
                    print(f'Removing file {row.filename}')
                    os.remove(row.filename)

            for row in fitted_out_spat_files:
                if os.path.exists(row.filename):
                    print(f'Removing file {row.filename}')
                    os.remove(row.filename)

            for row in fitted_out_speed_files:
                if os.path.exists(row.filename):
                    print(f'Removing file {row.filename}')
                    os.remove(row.filename)

            for row in fitted_images_spat_files:
                if os.path.exists(row.filename):
                    print(f'Removing file {row.filename}')
                    os.remove(row.filename)
                    
            for row in fitted_images_speed_files:
                if os.path.exists(row.filename):
                    print(f'Removing file {row.filename}')
                    os.remove(row.filename)
