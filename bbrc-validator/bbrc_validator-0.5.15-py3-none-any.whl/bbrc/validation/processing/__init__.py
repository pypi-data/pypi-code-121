def aget_cmap():
    import bbrc
    import numpy as np
    import os.path as op

    fn = 'FreeSurferColorLUT.txt'
    fp = op.join(op.dirname(bbrc.__file__), 'data', fn)
    data = open(fp).read().split('\n')
    lut = [[each for each in e.split(' ') if each != '']
           for e in data if not e.startswith('#') and len(e) != 0]
    LUT = {each[0]: [int(e) for e in each[2:5]] for each in lut}
    LUT = [LUT.get(str(i), [255, 255, 255]) for i in range(0, 2035)]
    LUT = np.array(LUT)
    LUT = LUT / 255.0
    return LUT


def probamap_snapshot(t1_fp, c1_fp):
    from nilearn import plotting
    import tempfile

    paths = []
    for each in 'xyz':
        _, path = tempfile.mkstemp(suffix='.jpg')
        paths.append(path)
        im = plotting.plot_anat(t1_fp, draw_cross=False, display_mode=each,
                                cut_coords=10)
        im.add_overlay(c1_fp)
        im.savefig(path)
    return paths


def topup_snapshot(pre_fp, post_fp):
    from nilearn import plotting, image
    import tempfile

    # compute a threshold for the overlay based on range of intensity values
    data = image.load_img(post_fp).get_fdata()
    val_range = abs(data.min()) + abs(data.max())
    thresh = val_range / 6

    paths = []
    for each in 'xyz':
        _, path = tempfile.mkstemp(suffix='.jpg')
        paths.append(path)
        im = plotting.plot_anat(pre_fp,
                                black_bg=True,
                                bg_img=None,
                                display_mode=each,
                                draw_cross=False,
                                cmap='black_green')
        im.add_overlay(post_fp,
                       threshold=thresh,
                       cmap='black_red')
        im.savefig(path)
    return paths


def ants_snapshot(t1w_fp, coreg_fp):
    from nilearn import plotting
    from nilearn import image
    import tempfile

    # compute a threshold for the overlay based on range of intensity values
    data = image.load_img(coreg_fp).get_fdata()
    val_range = abs(data.min()) + abs(data.max())
    thresh = val_range / 6

    paths = []
    for each in 'xyz':
        _, path = tempfile.mkstemp(suffix='.jpg')
        paths.append(path)
        im = plotting.plot_anat(t1w_fp,
                                black_bg=True,
                                bg_img=None,
                                display_mode=each,
                                draw_cross=False)
        im.add_overlay(coreg_fp,
                       threshold=thresh,
                       cmap=plotting.cm.black_red)
        im.savefig(path)
    return paths


def holes_snapshot(c2_fp, diff_fp):
    from nilearn import plotting
    import tempfile
    import os

    paths = []
    for each in 'xyz':
        f, path = tempfile.mkstemp(suffix='.png')
        paths.append(path)
        im = plotting.plot_anat(c2_fp,
                                black_bg=True,
                                bg_img=None,
                                display_mode=each,
                                draw_cross=False,
                                cut_coords=10,
                                cmap='green_transparent',
                                threshold=0.5)
        im.add_overlay(diff_fp, threshold=0.5, cmap='red_transparent')
        im.savefig(path)
        os.close(f)
    return paths


def __download_data__(xnat_instance, experiment_id, resource_name, fn=None):
    import tempfile
    from nisnap import xnat

    dl_functions = {'FREESURFER': xnat.__download_freesurfer__,
                    'SPM12': xnat.__download_spm12__,
                    'ASHS': xnat.__download_ashs__}
    kwargs = {'raw': True, 'cache': False}
    if fn:
        kwargs['fn'] = fn
    # Find the right download function from nisnap and download resources
    try:
        for short_name, __dl__ in dl_functions.items():
            if short_name in resource_name:
                filepaths = __dl__(xnat_instance, experiment_id,
                                   tempfile.gettempdir(), resource_name,
                                   **kwargs)
                break
        bg = filepaths.pop(0)
        if len(filepaths) == 1:
            filepaths = filepaths[0]

    except IndexError:
        msg = 'Downloading resources from XNAT failed. Check whether '\
              'experiment %s has valid resource %s on %s' \
              % (experiment_id, resource_name, xnat_instance._server)
        raise Exception(msg)
    return bg, filepaths


def __select_slices__(filepaths, axes, rowsize, figsize, step=1, threshold=0):
    import numpy as np
    import nibabel as nib
    from nisnap.utils import slices
    data = np.asarray(nib.load(filepaths).dataobj)

    rowsize = slices._fix_rowsize_(axes, rowsize)
    figsize = slices._fix_figsize_(axes, figsize)
    sl = slices.cut_slices(data, axes, rowsize, slices=None, step=step,
                           threshold=threshold)
    sl = {a: [item for sublist in sl[a] for item in sublist] for a in axes}
    return sl


class Snapshot:
    """
    This class can be derived to benefit from the `snap` function. This
    function generates a snapshot based on controlled parameters (`axes`,
    `rowsize` (# of slices per row per axis), `figsize` (figure dimensions per
    axis), `labels` (set of labels to include in the snapshot), `step`
    (increment between two consecutive slices), `n_slices` (# of slices per
    axis), `threshold` (# of voxels with non-null label one slice should have
    to get included in the final snapshot).

    Some others parameters are fixed in this version eg. `samebox`, `contours`
    or `opacity`.

    Uses nisnap to first download the data, select the proper slices and
    renders the snapshot. Returns the path to the resulting file.
    """
    axes = None
    rowsize = None
    figsize = None
    labels = None
    step = None
    n_slices = None
    threshold = None
    contours = True
    margin = 5

    def __init__(self):
        pass

    def run(self, experiment_id):
        import os
        from ..test import Results

        if os.getenv('SKIP_SNAPSHOTS_TESTS') == 'True':
            return Results(experiment_id == self.passing[0],
                           data=['Skipping it. (SKIP_SNAPSHOTS_TESTS)'])
        try:
            snap_fp = self.snap(experiment_id)
        except Exception:
            return Results(False, data=['Snapshot creation failed.'])

        return Results(True, data=[snap_fp])

    def report(self):
        report = []
        if self.results.has_passed:
            path = self.results.data[0]
            report.append('![snapshot](%s)' % path)
        else:
            report = self.results.data

        return report

    def snap(self, experiment_id):
        """
        Creates a snapshot of the given resource and returns the path to the
        created file.

        Returns:
            str: Path to the created snapshot.
        """

        from . import __download_data__, __select_slices__
        from nisnap import snap
        import tempfile
        import os
        kwargs = {'xnat_instance': self.xnat_instance,
                  'experiment_id': experiment_id,
                  'resource_name': self.resource_name}
        if hasattr(self, 'fn'):
            kwargs['fn'] = self.fn

        bg, filepaths = __download_data__(**kwargs)

        sl = __select_slices__(filepaths, self.axes, self.rowsize,
                               self.figsize, step=self.step,
                               threshold=self.threshold)
        slices = {}
        for a in self.axes:
            margin = int((len(sl[a]) - self.n_slices[a]) / 2.0)
            sx = sl[a][margin:len(sl[a]) - margin - 1]
            slices[a] = sx

        # Create snapshot with proper options
        fd, snap_fp = tempfile.mkstemp(suffix=snap.__format__)
        os.close(fd)

        snap.plot_segment(filepaths, axes=self.axes, bg=bg, opacity=70,
                          slices=slices, animated=False, savefig=snap_fp,
                          figsize=self.figsize, rowsize=self.rowsize,
                          contours=self.contours, samebox=True,
                          labels=self.labels, margin=self.margin)
        return snap_fp
