class BayesKMeansParameters(object):
    def __init__(self):
        self.bounds = [[2, 50]]
        self.__right_border = 50
        self.initial_point_generator = 'hammersly'
        self.n_init_points = 4
        self.acq_optimizer = 'lbfgs'
        self.acq_func = 'gp_hedge'
        self.xi = 0.01
        self.kappa = 5
        self.n_restarts_optimizer = 1
        self.noise = 'gaussian'
        self.dispersion = 7
        self.n_calls = 6
        self.x_0 = []
        self.y_0 = []
        self.elbow = []
        self.method = None

    def auto_set_params(self, persent='99'):
        disp = 4
        if persent == '95':
            disp = 4
        elif persent == '99':
            disp = 7
        else:
            print('Persent value can be "95" or "99", set to "95%"')
        self.initial_point_generator = 'hammersly'
        self.n_init_points = max(5 - int(self.__right_border / 50), 2)
        self.acq_optimizer = 'lbfgs'
        self.acq_func = 'gp_hedge'
        self.n_restarts_optimizer = 1
        self.noise = 'gaussian'
        self.dispersion = disp + int((self.__right_border - 50) / 100)
        self.n_calls = 2 + int(self.__right_border / 50) * 2 - 3 * int((self.__right_border - 50) / 100)

    def set_parameters(self, bounds=None, initial_point_generator=None, n_init_points=None, acq_optimizer=None,
                       acq_func=None, xi=None, kappa=None, n_restarts_optimizer=None, noise=None,
                       dispersion=None, n_calls=None):
        if bounds is not None:
            self.bounds = bounds
            self.__right_border = bounds[0][1]
        if initial_point_generator is not None:
            self.initial_point_generator = initial_point_generator
        if n_init_points is not None:
            self.n_init_points = n_init_points
        if acq_optimizer is not None:
            self.acq_optimizer = acq_optimizer
        if acq_func is not None:
            self.acq_func = acq_func
        if xi is not None:
            self.xi = xi
        if kappa is not None:
            self.kappa = kappa
        if n_restarts_optimizer is not None:
            self.n_restarts_optimizer = n_restarts_optimizer
        if noise is not None:
            self.noise = noise
        if dispersion is not None:
            self.xi = dispersion
        if n_calls is not None:
            self.xi = n_calls

