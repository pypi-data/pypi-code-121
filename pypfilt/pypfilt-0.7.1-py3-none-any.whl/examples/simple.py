import io
import numpy as np
import pkgutil
import pypfilt
import scipy


class GaussianWalk(pypfilt.Model):
    """A Gaussian random walk."""

    def init(self, ctx, vec):
        vec['x'] = ctx.data['prior']['x']

    def field_types(self, ctx):
        return [('x', np.dtype(float))]

    def update(self, ctx, t, dt, is_fs, prev, curr):
        """Perform a single time-step."""
        rnd = ctx.component['random']['model']
        curr['x'] = prev['x'] + rnd.uniform(size=curr.shape)

    def can_smooth(self):
        return {}


class GaussianObs(pypfilt.obs.Univariate):
    """A Gaussian observation model for the GaussianWalk model."""
    def __init__(self, obs_unit, settings):
        super().__init__(obs_unit)
        self.sdev = settings['parameters']['sdev']

    def distribution(self, ctx, snapshot, ixs=None):
        expected = snapshot.vec['state_vec']['x']
        if ixs is not None:
            expected = expected[ixs]
        return scipy.stats.norm(loc=expected, scale=self.sdev)


def __example_data(filename):
    return pkgutil.get_data('pypfilt.examples', filename).decode()


def gaussian_walk_toml_data():
    """Return the contents of the example file "gaussian_walk.toml"."""
    return __example_data('gaussian_walk.toml')


def gaussian_walk_instance():
    """
    Return an instance of the simple example scenario.
    """
    toml_input = io.StringIO(gaussian_walk_toml_data())
    instances = list(pypfilt.scenario.load_instances(toml_input))
    assert len(instances) == 1
    return instances[0]
