import numpy as np

from geodesic.utils import DeferredImport

plt = DeferredImport('matplotlib.pyplot')
mpl = DeferredImport('matplotlib')
animation = DeferredImport('matplotlib.animation')

display = DeferredImport('IPython.display')


def animate_tesseract(tesseract: np.ndarray, fig=None, figsize=(15, 8), scale_type='minmax', filename=None):
    backend_ = mpl.get_backend()
    mpl.use("Agg")  # Prevent showing stuff

    if tesseract.ndim != 4:
        raise ValueError(f"invalid dimensions({tesseract.ndim}), must be 4")

    if tesseract.shape[0] == 0:
        raise ValueError("no time values found")

    times, n_bands, rows, cols = tesseract.shape

    i = 0

    if scale_type == 'minmax':
        cmin = np.nanmin(tesseract)
        cmax = np.nanmax(tesseract)
    elif scale_type == "stddev":
        mu = np.nanmedian(tesseract)
        std = np.nanstd(tesseract)

        cmin = mu - std
        cmax = mu + std

        cmin = max(np.nanmin(tesseract), cmin)
        cmax = min(np.nanmax(tesseract), cmax)

    images = [plt.imshow(
        tesseract[0, i],
        animated=True,
        clim=(
            cmin,
            cmax,
        ),
        cmap='inferno'
    ) for i in range(n_bands)]

    def updatefig(*args):
        i = args[0] % len(tesseract)
        for im in images:
            im.set_array(tesseract[i, 0])
        i += 1
        return tuple(images)

    if fig is None:
        fig, _ = plt.subplots(1, n_bands, figsize=figsize)

    anim = animation.FuncAnimation(fig, updatefig, interval=100, fargs=(i,))
    if filename is not None:
        anim.save(filename)

    mpl.use(backend_)  # Reset backend
    try:
        return display.HTML(anim.to_html5_video())
    except ImportError:
        return anim.to_html5_video()
