import os
import shutil

import matplotlib.pyplot as plt
import tooltime


def save_figure(
    name=None,
    figure_dir=None,
    path=None,
    historical_dir=None,
    formats=None,
    png=None,
    svg=None,
    verbose=True,
):
    """save figure to mutiple formats and optionally archive at each save

    specify one of
    - {name, figure_dir}
    - {path}
    """

    # compute output formats
    paths = {}
    if path is not None:
        head, ext = os.path.splitext(path)
        if len(ext) > 0 and ext[0] == '.':
            paths = {ext[1:]: path}
    else:
        if formats is None:
            formats = []
            if svg:
                formats.append('svg')
            if png:
                formats.append('png')
            if len(formats) == 0:
                formats.append('png')
        if figure_dir is None or name is None:
            raise Exception('must specify path or (name and figure dir)')
        paths = {
            format: os.path.join(figure_dir, format, name + '.' + format)
            for format in formats
        }

    # gather kwargs
    save_kwargs = {'bbox_inches': 'tight'}

    # save figure to each format
    for path in paths.values():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if verbose:
            print('saving figure ' + name + ':', path)
        plt.savefig(path, **save_kwargs)

    # copy to historical dir
    if historical_dir is not None:
        timestamp = tooltime.create_timestamp_label()
        historical_name = timestamp + '__' + name + '.'
        for format in formats:
            path = os.path.join(figure_dir, format, historical_name + format)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            shutil.copy(paths[format], path)
