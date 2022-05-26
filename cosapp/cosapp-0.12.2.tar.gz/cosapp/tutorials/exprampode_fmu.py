from cosapp.base import System

class ExpRampOde(System):
    """
    System representing function f(t) = a * (1 - exp(-t / tau)),
    through ODE: tau * f' + f = a
    
    f is then apply on an input signal x to produce y.
    """
    def setup(self):
        self.add_inward('a', 1.0)
        self.add_inward('tau', 1.0)
        self.add_inward('x', 1.0)
        self.add_outward('y', 1.0)

        self.add_outward('df_dt', 0.0)
        self.add_transient('f', der='df_dt', max_time_step='tau / 5')

    def compute(self):
        self.df_dt = (self.a - self.f) / self.tau
        self.y = self.x * self.f
