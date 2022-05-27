import ovito
from ..data import DataCollection, DataObject
from ..pipeline import Pipeline, StaticSource
from ..nonpublic import AttributeFileExporter, PipelineStatus, PipelineObject

def export_file(data, file, format, **params):
    """ Writes data to an output file. See section :ref:`file_output_overview` for an overview.

        :param data: The object to be exported. See available options below.
        :param str file: The output file path.
        :param str format: The kind of file to write. See available options below.
        :param params: Optional keyword arguments depending on the selected format. 

        **Data to be exported**

        The following things are acceptable as first argument:

        :py:class:`~ovito.pipeline.Pipeline`
            If you provide a data pipeline, the dynamically computed output of the pipeline is exported. Since pipelines support evaluation at different animation times,
            a sequence of frames can be exported by passing the keyword argument ``multiple_frames=True``, see below.

        :py:class:`~ovito.data.DataCollection`
            If you specify a data collection, the static snapshot stored in the collection is exported. 
            Note that it depends on the selected file format which objects from the data collection will be exported.

        :py:class:`~ovito.data.DataObject`
            If you specify a single data object, e.g. a :py:class:`~ovito.data.DataTable` or :py:class:`~ovito.data.SurfaceMesh`,
            just that one object is exported. The behavior is similar to providing a :py:class:`~ovito.data.DataCollection` 
            containing a single data object.

        `None`
            In this case the output of all data pipelines in the current visualization scene (see :py:attr:`ovito.Scene.pipelines` list) 
            is exported to a single file. This option is only supported for the POV-Ray export format, which stores a full scene 
            description.

        Additional keyword parameters, as documented below, let you select the aspects of a dataset to be written to the output file.
        For instance, for some file formats the ``columns`` keyword controls the set of particle properties to be saved.

        **Output filename**

        The parameter *file* specifies the path of the output file. If the filename ends with the suffix `.gz`,
        the output file will be compressed using the zlib library to save disk space (works only for text-based file formats).

        If a wildcard "*" character appears in the filename, then one file per animation frame is written and the "*" character is replaced 
        with the frame number. This feature is typically used in conjunction with the ``multiple_frames=True`` option, see below.

        **Output formats**

        The parameter *format* selects the kind of file to write:

        ============================= ======================================================================== 
        Format string                 Description              
        ============================= ======================================================================== 
        ``"txt/attr"``                Export global attributes to a text file (see below)
        ``"txt/table"``               Export a :py:class:`~ovito.data.DataTable` to a text file
        ``"lammps/dump"``             LAMMPS text-based dump format
        ``"lammps/data"``             LAMMPS data format
        ``"imd"``                     IMD format
        ``"vasp"``                    POSCAR format
        ``"xyz"``                     XYZ format
        ``"fhi-aims"``                FHI-aims format
        ``"gsd/hoomd"``               GSD format used by the HOOMD simulation code
        ``"netcdf/amber"``            Binary format for MD data following the `AMBER format convention <https://ambermd.org/netcdf/nctraj.pdf>`__
        ``"vtk/trimesh"``             `ParaView VTK format <https://www.vtk.org/VTK/img/file-formats.pdf>`__ for exporting :py:class:`~ovito.data.SurfaceMesh` objects
        ``"vtk/disloc"``              `ParaView VTK format <https://www.vtk.org/VTK/img/file-formats.pdf>`__ for exporting :py:class:`~ovito.data.DislocationNetwork` objects
        ``"vtk/grid"``                `ParaView VTK format <https://www.vtk.org/VTK/img/file-formats.pdf>`__ for exporting :py:class:`~ovito.data.VoxelGrid` objects
        ``"ca"``                      :ref:`Text-based format for storing dislocation lines <manual:particles.modifiers.dislocation_analysis.fileformat>`
        ``"povray"``                  `POV-Ray <https://www.povray.org/>`__ scene format
        ============================= ========================================================================

        Depending on the selected output format, additional keyword arguments may be passed to :py:func:`!export_file` as documented in the following sections.

        **File columns**

        For the output formats *lammps/dump*, *xyz*, *imd*, and *netcdf/amber* you must specify the set of particle properties to export
        by providing the ``columns`` keyword parameter::

            export_file(pipeline, "output.xyz", "xyz", columns =
              ["Particle Identifier", "Particle Type", "Position.X", "Position.Y", "Position.Z"])

        In case of vector properties, one of the property's :py:attr:`~ovito.data.Property.component_names` must be appended 
        to the base name, e.g. `Position.Z` or `Atomic Strain.XY`. See the list of :ref:`standard particle properties <particle-properties-list>`.

        .. tip::

            If you are not sure which particle properties are available for export, you can print the list of properties 
            produced by your current data pipeline to the console::

               print(pipeline.compute().particles)

        **Exporting several simulation frames**

        By default, only the current animation frame (frame 0 by default) is exported.
        To export a different trajectory frame, pass the ``frame`` keyword parameter to the :py:func:`!export_file` function.
        Alternatively, you can export all frames of the animation sequence at once by specifying ``multiple_frames=True``. 
        More refined control is possible through the keyword arguments ``start_frame``, ``end_frame``, and ``every_nth_frame``.

        Some file formats such as *lammps/dump*, *xyz*, *gsd/hoomd* or *netcdf/amber* can store all frames of the exported trajectory 
        in a single output file. For other formats, or if you prefer one file per frame, you must pass a filename pattern 
        to :py:func:`!export_file`. The specified output filename must contain a ``*`` wildcard character as in the following example, 
        which will be replaced with the animation frame number during export::

            export_file(pipeline, "output.*.dump", "lammps/dump", multiple_frames=True)

        This is equivalent to an explicit for-loop that exports the frames one by one to a series of files::

            for i in range(pipeline.source.num_frames):
                export_file(pipeline, f"output.{i}.dump", "lammps/dump", frame=i)

        **Floating-point number precision**

        For text-based file formats, you can specify the desired formatting precision for floating-point values using the
        ``precision`` keyword parameter. The default output precision is 10 digits; the maximum is 17.

        **LAMMPS atom style**

        When writing files in the *lammps/data* format, the LAMMPS atom style "atomic" is used by default. If you want to output
        a data file with a different `LAMMPS atom style <https://docs.lammps.org/atom_style.html>`__, specify it using the ``atom_style`` keyword parameter::

            export_file(pipeline, "output.data", "lammps/data", atom_style="bond")
            export_file(pipeline, "output.data", "lammps/data", atom_style="hybrid", atom_substyles=("template", "charge"))

        If at least one :py:class:`~ovito.data.ParticleType` of the exported model has a non-zero :py:attr:`~ovito.data.ParticleType.mass` value,
        OVITO writes a ``Masses`` section to the LAMMPS data file. You can suppress it by passing ``omit_masses=True`` to the export function.
        Furthermore, the keyword argument ``ignore_identifiers=True`` replaces any existing atom IDs (particle property `Particle Identifier`) 
        with a contiguous sequence of numbers during file export.

        **VASP (POSCAR) format**

        When exporting to the *vasp* file format, OVITO will output atomic positions and velocities in Cartesian coordinates by default.
        You can request output in reduced cell coordinates by specifying the ``reduced`` keyword parameter::

            export_file(pipeline, "structure.poscar", "vasp", reduced=True)

        **Global attributes**

        The *txt/attr* file format allows you to write global quantities computed by the data pipeline to a text file.
        For example, here is how you export the number of FCC atoms identified by a :py:class:`~ovito.modifiers.CommonNeighborAnalysisModifier`
        as a function of simulation time to a simple text file::

            export_file(pipeline, "data.txt", "txt/attr",
                columns=["Timestep", "CommonNeighborAnalysis.counts.FCC"],
                multiple_frames=True)

        .. tip::

            If you are not sure which global attributes are available for export, you can print the list of :py:attr:`~ovito.data.DataCollection.attributes`
            produced by your current data pipeline to the console::

               print(pipeline.compute().attributes)

    """

    # Determine the animation frame(s) to be exported.
    if 'frame' in params:
        frame = int(params['frame'])
        params['multiple_frames'] = True
        params['start_frame'] = frame
        params['end_frame'] = frame
        del params['frame']

    # Look up the exporter class for the selected format.
    if not format in export_file._formatTable:
        raise RuntimeError("Unknown output file format: %s" % format)

    # Create an instance of the exporter class.
    exporter = export_file._formatTable[format](params)

    # Pass function parameters to exporter object.
    exporter.output_filename = file

    # Detect wildcard filename.
    if '*' in file:
        exporter.wildcard_filename = file
        exporter.use_wildcard_filename = True

    # Exporting to a file is a long-running operation, which is not permitted during viewport rendering or pipeline evaluation.
    # In these situations, the following function call will raise an exception.
    ovito.scene.request_long_operation()

    # Pass data to be exported to the exporter:
    if isinstance(data, Pipeline):
        exporter.pipeline = data
    elif isinstance(data, PipelineObject):
        exporter.pipeline = Pipeline(source = data)
    elif isinstance(data, DataCollection):
        exporter.pipeline = Pipeline(source = StaticSource(data = data))
    elif isinstance(data, DataObject):
        data_collection = DataCollection()
        data_collection.objects.append(data)
        exporter.pipeline = Pipeline(source = StaticSource(data = data_collection))
        exporter.key = data.identifier
    elif data is None:
        exporter.select_default_exportable_data()
    else:
        raise TypeError(f"Invalid data. Cannot export this kind of Python object: {data}")

    # Automatically adjust frame interval to length of exportable trajectory.
    if exporter.multiple_frames:
        # This method will fetch the length of the trajectory from the pipeline and use it to set
        # the export interval. We also check whether the user has specified explicit interval bounds.
        exporter.determine_export_interval(not 'start_frame' in params, not 'end_frame' in params)

    # Let the exporter do its job.
    exporter.do_export()
ovito.io.export_file = export_file

# This is the table of export formats used by the export_file() function
# to look up the right exporter class for a file format.
# Plugins can register their exporter class by inserting a new entry in this dictionary.
export_file._formatTable = {}
export_file._formatTable["txt/attr"] = AttributeFileExporter