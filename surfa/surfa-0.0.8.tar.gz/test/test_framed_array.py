import pytest
import numpy as np
import surfa as sf


def basedim_to_framed_type(basedim):
    atype = {
        # 1: sf.Overlay,
        2: sf.Slice,
        3: sf.Volume,
    }.get(basedim)
    if atype is None:
        raise ValueError(f'Unsupported FramedArray dimensions: {basedim}')
    return atype


def test_data_management():
    """
    TODOC
    """

    na = np.random.rand(16, 16, 16)
    fa = sf.Volume(na)
    assert na is fa.data

    fac = sf.Volume(fa)
    assert fac.data is fa.data

    fac = sf.Volume(fa.copy())
    assert fac.data is not fa.data

    fac = fa.copy()
    assert fac.data is not fa.data


def test_data_shapes():
    """
    TODOC
    """

    for dim in (2, 3):  # TODO make overlay...

        BaseClass = basedim_to_framed_type(dim)

        # TODOC
        baseshape = tuple([32] * dim)
        fa = BaseClass(np.zeros(baseshape))
        assert fa.basedim == dim
        assert fa.nframes == 1
        assert fa.shape == baseshape
        assert fa.baseshape == baseshape
        assert fa.data.shape == baseshape
        assert fa.framed_data.shape == (*baseshape, 1)

        # TODOC
        nframes = 4
        shape = (*baseshape, nframes)
        fa = BaseClass(np.zeros(shape))
        assert fa.basedim == dim
        assert fa.nframes == nframes
        assert fa.shape == shape
        assert fa.baseshape == baseshape
        assert fa.data.shape == shape
        assert fa.framed_data.shape == shape

        # TODOC
        for x in np.arange(1, dim):
            inshape = tuple([8] * x)
            fa = BaseClass(np.zeros(inshape))
            outshape = np.ones(dim)
            outshape[:x] = inshape
            outshape = tuple(outshape)
            assert fa.basedim == dim
            assert fa.nframes == 1
            assert fa.shape == outshape
            assert fa.baseshape == outshape

        # TODOC
        with pytest.raises(ValueError):
            BaseClass(np.asarray(0))

        # TODOC
        for x in np.arange(3):
            with pytest.raises(ValueError):
                BaseClass(np.zeros(tuple([8] * (dim + 2 + x))))


def test_operators_and_assignment():
    """
    Super tedious, low-level test to make sure python math operators mimic
    the numpy standard. If these tests fail, then there are some big problems.
    """

    def array_equal(a, b, expected=sf.core.framed_array.FramedArray):
        assert isinstance(a, expected)
        assert isinstance(b, np.ndarray)
        assert a.shape == b.shape
        assert a.dtype == b.dtype
        assert np.array_equal(a, b)

    # test for all possible dimensions
    # for dim in (1, 2, 3):
    for dim in (2, 3):

        BaseClass = basedim_to_framed_type(dim)

        # generate a random numpy array, copy it, and initialize a FramedArray.
        # anything done to the FramedArray should match the numpy array exactly.
        shape = tuple([32] * dim)
        na = np.random.rand(*shape)
        fa = BaseClass(na.copy())

        # unary operators
        array_equal(+fa, +na)
        array_equal(-fa, -na)

        # binary operators
        array_equal(fa ** 3, na ** 3)
        array_equal(fa + 0.5, na + 0.5)
        array_equal(fa - 0.5, na - 0.5)
        array_equal(fa * 0.5, na * 0.5)
        array_equal(fa / 0.5, na / 0.5)

        # reverse binary operators
        array_equal(0.5 + fa, 0.5 + na)
        array_equal(0.5 - fa, 0.5 - na)
        array_equal(0.5 * fa, 0.5 * na)
        array_equal(0.5 / fa, 0.5 / na)

        # binary operators with numpy array
        nr = np.random.rand(*na.shape)
        array_equal(fa + nr, na + nr)
        array_equal(fa - nr, na - nr)
        array_equal(fa * nr, na * nr)
        array_equal(fa / nr, na / nr)

        # binary operators with framed array
        fr = BaseClass(nr.copy())
        array_equal(fa + fr, na + nr)
        array_equal(fa - fr, na - nr)
        array_equal(fa * fr, na * nr)
        array_equal(fa / fr, na / nr)

        # reverse binary operators with numpy array
        array_equal(nr + fa, nr + fa, expected=np.ndarray)
        array_equal(nr - fa, nr - fa, expected=np.ndarray)
        array_equal(nr * fa, nr * fa, expected=np.ndarray)
        array_equal(nr / fa, nr / fa, expected=np.ndarray)

        x = na.flatten()[10]  # grab some arbitrary element
        scaling = np.random.rand(4)
        for factor in (1, nr, fr):

            # assignment operators
            fab = fa.copy()
            nab = na.copy()
            fab += scaling[0] * factor
            nab += scaling[0] * factor
            fab -= scaling[1] * factor
            nab -= scaling[1] * factor
            fab *= scaling[2] * factor
            nab *= scaling[2] * factor
            fab /= scaling[3] * factor
            nab /= scaling[3] * factor
            array_equal(fab, nab)

            # comparisons
            array_equal(fa == x, na == x)
            array_equal(fa != x, na != x)
            array_equal(fa <= x, na <= x)
            array_equal(fa >= x, na >= x)

        # more comparisons
        fab = (fa < 0.5) & (fa > 0.2) | (fa > 0.8)
        nab = (na < 0.5) & (na > 0.2) | (na > 0.8)
        array_equal(fab, nab)


def test_data_functions():
    """
    TODOC
    """

    fa = sf.Volume(np.random.rand(16, 16, 16, 2))

    assert fa.max() == fa.data.max()
    assert fa.min() == fa.data.min()
    assert fa.mean() == fa.data.mean()
    assert fa.min(nonzero=True) == fa.data[fa.data != 0].min()
    assert fa.mean(nonzero=True) == fa.data[fa.data != 0].mean()

    # TODO update for newer numpy
    p = [0.2, 0.4, 0.6, 0.8]
    for method in ('linear', 'midpoint'):
        assert np.array_equal(fa.percentile(p, method=method),
                              np.percentile(fa.data, p, interpolation=method))
        assert np.array_equal(fa.percentile(p, method=method, nonzero=True),
                              np.percentile(fa.data[fa.data != 0], p, interpolation=method))
