import copy


def linear_grid(min_val, max_val, delta):
    """Linear grid."""
    if isinstance(delta, int):
        n = delta
        if n > 1:
            delta = (max_val - min_val) / (n-1)
        else:
            delta = 0.0
    else:
        n = int((max_val - min_val) / delta) + 1
    return [min_val + i*delta for i in range(n)]


def logx_grid(x1, x2, n):
    """Create a list of n numbers in logx scale from x1 to x2."""
    # the shape if a*x^n. if n=0 => a=x1, if n=N => x1*x^N=x2
    if x1 > 0:
        xx = (x2 / x1)**(1.0 / n)
        return [x1] + [x1 * xx**(i+1) for i in range(1, n)]
    else:
        xx = x2**(1.0/n)
        return [x1] + [xx**(i+1) - 1 for i in range(1, n)]


def ifabsmm(x, f):
    """
    Find absolute maximum and absolute minimum of f(x) using a
    parabolic interpolation.

    Given x and f(x), the function returns a tuple of two entries, the
    first one being (x_min, f(x_min)), the second (x_max, f(x_max)).

    If the maximum of the minimum lies on the boundary of the
    interval, no interpolation is performed.
    """

    def _vertex_parabola(a, b, c):
        """Returns the vertex (x,y) of a parabola of the type a*x**2 + b*x + c."""
        return -b/(2*a), - (b**2 - 4*a*c) / (4*a)

    def _parabola_3points(x1, y1, x2, y2, x3, y3):
        """Parabola through 3 points."""
        delta = (x1 - x2)*(x1 - x3)*(x2 - x3)
        a = (x3 * (y2 - y1) + x2 * (y1 - y3) + x1 * (y3 - y2)) / delta
        b = (x3**2 * (y1 - y2) + x2**2 * (y3 - y1) + x1**2 * (y2 - y3)) / delta
        c = (x2 * x3 * (x2 - x3) * y1 + x3 * x1 * (x3 - x1) * y2 + x1 * x2 * (x1 - x2) * y3) / delta
        return a, b, c

    # First uninterpolated minima and maxima
    f = list(f)
    imin, imax = f.index(min(f)), f.index(max(f))
    # Then perform parabolic interpolation
    ii = []
    for i in [imin, imax]:
        if i == len(f)-1 or i == 0:
            # At boundaries we do nothing
            ii.append((x[i], f[i]))
        else:
            # Parabola around i
            i1, i2, i3 = i-1, i, i+1
            a, b, c = _parabola_3points(x[i1], f[i1], x[i2], f[i2], x[i3], f[i3])
            ii.append(_vertex_parabola(a, b, c))
    return ii[0], ii[1]


def linear_fit(xdata, ydata):
    """
    Linear regression.

    Expressions as in Wikipedia (https://en.wikipedia.org/wiki/Simple_linear_regression)
    """
    import numpy
    from math import sqrt

    n = len(ydata)
    dof = n - 2
    sx = numpy.sum(xdata)
    sy = numpy.sum(ydata)
    sxy = sum(xdata * ydata)
    sxx = sum(xdata**2)
    syy = sum(ydata**2)

    a = (n * sxy - sx * sy) / (n * sxx - sx**2)
    b = sy / n - a * sx / n
    if dof > 0:
        s = (n*syy - sy**2 - a**2 * (n*sxx - sx**2)) / (n*dof)
    else:
        s = 0.0
    sa = n * s / (n*sxx - sx**2)
    sb = sa * sxx / n
    return a, b, sqrt(sa), sqrt(sb)


def feqc(x, f, fstar):
    """
    Find first root of f=f(x) for data sets.

    Given two lists x and f, it returns the value of xstar for which
    f(xstar) = fstar. Raises an ValueError if no root is found.
    """
    s = f[0] - fstar
    for i in range(min(len(x), len(f))):
        if (f[i] - fstar) * s < 0.0:
            # Linear interpolation
            dxf = (f[i] - f[i-1]) / (x[i] - x[i-1])
            xstar = x[i-1] + (fstar - f[i-1]) / dxf
            istar = i
            return xstar, istar

    # We get to the end and cannot find the root
    return None, None


def filter_species(system, species):
    """Callback to filter particles by species.

    The input species can be an integer (particle id), a string
    (particle name), or None. In this latter case, all particles
    are returned.
    """
    s = copy.copy(system)
    if species is not None:
        s.particle = [p for p in system.particle if p.species == species]
    return s


def copy_field(system, field, trajectory):
    """
    Copy particle property `field` from `trajectory` at the current
    frame in system.

    It requires atooms >= 1.10.0
    """
    # Only available in atooms > 1.10.0
    so = trajectory[system.frame]
    for p, po in zip(system.particle, so.particle):
        x = getattr(po, field)
        setattr(p, field, x)
    return system


def adjust_skip(trajectory, n_origins=None):
    """
    Define interval between frames in trajectory so as to achieve a
    given number of time origins.

    Possible values of n_origins:
    - None: heuristics to keep the product of steps * particles constant
    - int: if -1, all origins are used, otherwise if n_origins >= 1 only n_origins
    - float in the interval (0,1): the fraction of samples to consider as time origins
    """
    if n_origins is not None:
        if float(n_origins) < 0 or n_origins == '1.0':
            skip = 1 * trajectory.block_size  # all origins
        elif float(n_origins) > 1:
            nbl = len(trajectory.steps) // trajectory.block_size
            skip = int(nbl / float(n_origins)) * trajectory.block_size
        elif int(n_origins) == 1:
            skip = len(trajectory.steps)
        else:
            # A float between 0 and 1
            skip = int(1 / float(n_origins)) * trajectory.block_size
    else:
        # Heuristics (to be improved)
        if trajectory.block_size == 1:
            block = 40000
            # Ignore cache here
            # This destroys the connection between decorated unfolded trajectory and folded trajectory
            # _cache, trajectory.cache = trajectory.cache, False
            skip = int(len(trajectory.steps) * len(trajectory[0].particle) / block)
            # trajectory.cache = _cache
        else:
            # We stick to the block size
            skip = trajectory.block_size

    # Make sure the skip is an multiple of block size
    if skip % trajectory.block_size != 0 and int(n_origins) != 1:
        raise ValueError('wrong skip {} {}'.format(skip, trajectory.block_size))

    # Normalize anyway and make it even
    skip = max(1, skip)
    skip = min(len(trajectory.steps), skip)
    return skip


def _templated(entry, template, keep_multiple=False):
    """
    Filter a list of entries so as to best match an input
    template. Lazy, slow version O(N*M).

    Example:
    --------
    entry = [1,2,3,4,5,10,20,100]
    template = [1,7,12,80]
    templated(entry, template) == [1,5,10,100]
    """
    match = []
    for t in template:
        def compare(x):
            return abs(x - t)
        match.append(min(entry, key=compare))
    if not keep_multiple:
        match = list(set(match))
    return sorted(match)


def setup_t_grid(trajectory, t_grid, offset=True):
    # First get all possible time differences
    steps = trajectory.steps
    off_samp = {}
    if offset:
        offset_range = range(trajectory.block_size)
    else:
        offset_range = [0]
    for off in offset_range:
        for i in range(off, len(steps)-off):
            if steps[i] - steps[off] not in off_samp:
                off_samp[steps[i] - steps[off]] = (off, i-off)

    # Retain only those pairs of offsets and sample
    # difference that match the desired input. This is the grid
    # used internally to calculate the time correlation function.
    i_grid = set([int(round(t/trajectory.timestep)) for t in t_grid])
    offsets = [off_samp[t] for t in _templated(sorted(off_samp.keys()), sorted(i_grid))]
    return offsets


def _dump(title, columns=None, command=None, version=None,
          description=None, note=None, parents=None, inline=False,
          comment='# ', extra_fields=None):
    """
    Return a string of comments filled with metadata.
    """
    import datetime

    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if columns is not None:
        columns_string = ', '.join(columns)

    metadata = [('title', title),
                ('columns', columns_string),
                ('date', date),
                ('command', command),
                ('version', version),
                ('parents', parents),
                ('description', description),
                ('note', note)]

    if extra_fields is not None:
        metadata += extra_fields

    if inline:
        fmt = '{}: {};'
        txt = comment + ' '.join([fmt.format(key, value) for key,
                                  value in metadata if value is not None])
    else:
        txt = ''
        for key, value in metadata:
            if value is not None:
                txt += comment + '{}: {}\n'.format(key, value)
    return txt
