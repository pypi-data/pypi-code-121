from cosapp.base import System
import numpy as np


class PointDynamics1D(System):
    """Point mass dynamics in 1D using scalars"""
    def setup(self):
        self.add_inward("mass", 1.0, unit='kg')
        self.add_inward("acc_ext", 0.0, unit='m/s**2')
        self.add_inward("force_ext", 0.0, unit='N')

        self.add_outward("force", 0.0, unit='m/s**2')
        self.add_outward("acc", 0.0, unit='N')

    def compute(self):
        self.force = self.force_ext + self.mass * self.acc_ext
        self.acc = self.force / self.mass


class PointDynamics(System):
    """Point mass dynamics"""
    def setup(self):
        self.add_inward("mass", 1.0, unit='kg')
        self.add_inward("acc_ext", unit='m/s**2')
        self.add_inward("force_ext", unit='N')

        self.add_outward("force", unit='m/s**2')
        self.add_outward("acc", unit='N')

    def compute(self):
        self.force = self.force_ext + self.mass * self.acc_ext
        self.acc = self.force / self.mass


class PointFriction(System):
    """Point mass ~ v^2 friction model"""
    def setup(self):
        self.add_inward('v', desc="Velocity")
        self.add_inward('cf', 0.1, desc="Friction coefficient")

        self.add_outward("force", unit='N')

    def compute(self):
        self.force = (-self.cf * np.linalg.norm(self.v)) * self.v


class PointMass(System):
    def setup(self, g=[0, 0, -9.81]):
        self.add_child(PointFriction('friction'), pulling=['cf', 'v'])
        self.add_child(PointDynamics('dynamics'), pulling={
            'mass': 'mass',
            'force': 'force',
            'acc_ext': 'g',
            'acc': 'a',
        })
        self.exec_order = ['friction', 'dynamics']

        self.connect(self.friction, self.dynamics, {"force": "force_ext"})

        self.g = np.array(g)
        self.v = np.zeros_like(g)
        self.run_once()  # propagate values to initialize array dimensions

        self.add_transient('v', der='a')
        self.add_transient('x', der='v')


class BouncingBall(System):
    """Bouncing point mass"""
    def setup(self, g=[0, 0, -9.81]):
        self.add_child(PointMass('point', g=g), pulling=[
            'x', 'v', 'a', 'mass', 'cf', 'g',
        ])
        self.add_event('rebound', trigger="x[-1] <= 0")
        self.add_inward('cr', 1.0, desc="Rebound restitution coefficient", limits=(0, 1))
        self.add_outward_modevar("n_rebounds", init=0, dtype=int)

    def transition(self):
        cr = max(0, min(self.cr, 1))
        if self.rebound.present:
            self.n_rebounds += 1
            v = self.v
            if abs(v[-1]) < 1e-6:
                v[-1] = 0
            else:
                v[-1] *= -cr
