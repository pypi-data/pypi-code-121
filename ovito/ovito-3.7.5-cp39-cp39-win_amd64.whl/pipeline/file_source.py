import ovito
from . import FileSource
from ..data import DataCollection
from ..nonpublic import FileImporter, PipelineStatus
import collections.abc as collections

# Implementation of FileSource.load() method:
def _FileSource_load(self, location, **params):
    """ Sets a new input file, from which this data source will retrieve its data from.

        The function accepts additional keyword arguments, which are forwarded to the format-specific file reader.
        For further information, please see the documentation of the :py:func:`~ovito.io.import_file` function,
        which has the same function interface as this method.

        :param str location: The local file(s) or remote URL to load.
    """

    # Process input parameter
    if isinstance(location, str):
        location_list = [location]
    elif isinstance(location, collections.Sequence):
        location_list = list(location)
    else:
        raise TypeError("Invalid input file location. Expected string or sequence of strings.")
    first_location = location_list[0]

    # Importing a file is a long-running operation, which is not permitted during viewport rendering or pipeline evaluation.
    # In these situations, the following function call will raise an exception.
    ovito.scene.request_long_operation()

    # Did the caller specify the format of the input file explicitly?
    if 'input_format' in params:
        # Look up the importer class for the registered format name.
        format = params.pop('input_format')
        if not format in ovito.io.import_file._formatTable:
            raise ValueError("Unknown input format: '{}'. The supported formats are: {}".format(format, sorted(list(ovito.io.import_file._formatTable.keys()))))

        # Create an instance of the importer class. It will be configured below.
        importer = ovito.io.import_file._formatTable[format]()
    else:
        # Auto-detect the file's format if caller did not specify the format explicitly.
        importer = FileImporter.autodetect_format(self.dataset, first_location)
        if not importer:
            raise RuntimeError("Could not detect the file format. The format might not be supported.")

    # Re-use existing importer if compatible.
    if self.importer and type(self.importer) == type(importer):
        importer = self.importer

    # Forward user parameters to the importer.
    for key in params:
        if not hasattr(importer, key):
            raise RuntimeError("Importer object %s does not have an attribute '%s'." % (importer, key))
        importer.__setattr__(key, params[key])

    # Load new data file.
    if not self.set_source(location_list, importer, False, False):
        raise RuntimeError("Operation has been canceled by the user.")

    # Block execution until data file has been loaded.
    if not self.wait_until_ready(0): # Requesting frame 0 here, because full list of frames is not loaded yet at this point.
        raise RuntimeError("Operation has been canceled by the user.")

    # Raise Python error if loading failed.
    if self.status.type == PipelineStatus.Type.Error:
        raise RuntimeError(self.status.text)

    # Block until list of animation frames has been loaded
    if not self.wait_for_frames_list():
        raise RuntimeError("Operation has been canceled by the user.")

FileSource.load = _FileSource_load

# Implementation of FileSource.source_path property.
def _get_FileSource_source_path(self):
    """ This read-only attribute returns the path(s) or URL(s) of the file(s) where this :py:class:`!FileSource` retrieves its input data from.
        You can change the source path by calling :py:meth:`.load`. """
    path_list = self.get_source_paths()
    if len(path_list) == 1: return path_list[0]
    elif len(path_list) == 0: return ""
    else: return path_list
FileSource.source_path = property(_get_FileSource_source_path)

def _FileSource_compute(self, frame = None):
    """ Requests data from this data source. The :py:class:`!FileSource` will load it from the external file if needed.

        The optional *frame* parameter determines the frame to retrieve, which must be in the range 0 through (:py:attr:`num_frames`-1).
        If no frame number is specified, the current time slider position is used (will always be frame 0 for scripts not running in the context of an interactive OVITO session).

        The :py:class:`!FileSource` uses a caching mechanism to keep the data for one or more frames in memory. Thus, invoking :py:meth:`!compute`
        repeatedly to retrieve the same frame will typically be very fast.

        :param int frame: The source frame to retrieve.
        :return: A new :py:class:`~ovito.data.DataCollection` containing the loaded data.
    """
    if frame is not None:
        time = self.source_frame_to_anim_time(frame)
    else:
        time = self.dataset.anim.time

    state = self._evaluate(time)
    if state.status.type == PipelineStatus.Type.Error:
        raise RuntimeError("Data source evaluation failed: %s" % state.status.text)
    if not state.data:
        raise RuntimeError("Data pipeline did not yield any output DataCollection.")

    return state.mutable_data

FileSource.compute = _FileSource_compute