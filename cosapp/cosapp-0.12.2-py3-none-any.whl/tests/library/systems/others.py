import abc
import logging
from typing import Optional

import numpy as np

from cosapp.systems import SystemFamily, System
from cosapp.core.numerics.root import root
from cosapp.core.numerics.residues import Residue
from cosapp.tests.library.ports import FluidPort, MechPort, FluidState, FlowPort

logger = logging.getLogger(__name__)


class TurbofanFamily(SystemFamily, abc.ABC):

    def __init__(self, name: str):
        super(TurbofanFamily, self).__init__(name)

        self.family_name = 'Turbofan'
        self.modelings.add('SimpleTurbofan', fidelity=0.4, cost=0.2)
        self.modelings.add('AdvancedTurbofan', fidelity=0.5, cost=0.4)
        self.modelings.add('ComplexTurbofan', fidelity=0.45, cost=0.6)


class PlossFamily(SystemFamily, abc.ABC):

    def __init__(self, name: str):
        super(PlossFamily, self).__init__(name)

        self.family_name = 'Pressure loss'
        self.modelings.add('Duct', 0.4, 0.2)
        self.modelings.add('ComplexDuct', 0.4, 0.5)
        self.modelings.add('SerialDuct', 0.45, 0.4)


class Duct(PlossFamily):

    def setup(self):
        self.add_input(FluidPort, 'fl_in')
        self.add_output(FluidPort, 'fl_out', )
        self.add_inward('A', 1.)
        self.add_inward('cst_loss', 0.98)
        self.add_inward('glp', 0.05)
        self.add_outward('PR')

    def compute(self):
        wr = self.fl_in.W * (self.fl_in.Tt / 288.15) ** 0.5 / (self.fl_in.Pt / 101325)

        self.fl_out.Pt = self.cst_loss * self.fl_in.Pt
        self.fl_out.W = self.fl_in.W
        self.fl_out.Tt = self.fl_in.Tt

        self.PR = self.fl_out.Pt / self.fl_in.Pt

    def Duct_to_ComplexDuct(self):
        rtn = ComplexDuct(self.name)
        rtn.parent = self.parent
        rtn.duct.inwards.cst_loss = self.inwards.cst_loss
        rtn.bleed.split_ratio = 1.

        self.update_connections(rtn)
        return rtn

    def Duct_to_SerialDuct(self):
        rtn = SerialDuct(self.name)
        rtn.parent = self.parent
        rtn.duct1.inwards.cst_loss = self.inwards.cst_loss / 2
        rtn.duct2.inwards.cst_loss = self.inwards.cst_loss / 2

        self.update_connections(rtn)
        return rtn


class SerialDuct(PlossFamily):
    def setup(self):
        self.add_input(FluidPort, 'fl_in')
        self.add_output(FluidPort, 'fl_out')

        self.add_child(Duct('duct1'))
        self.add_child(Duct('duct2'))

        self.connect(self.fl_in, self.duct1.fl_in)
        self.connect(self.fl_out, self.duct2.fl_out)

        self.connect(self.duct1.fl_out, self.duct2.fl_in)

        self.exec_order = ['duct1', 'duct2']

    def SerialDuct_to_Duct(self):
        rtn = Duct(self.name)
        rtn.parent = self.parent
        rtn.inwards.cst_loss = self.duct1.inwards.cst_loss + self.duct2.inwards.cst_loss

        self.update_connections(rtn)
        return rtn

    def SerialDuct_to_ComplexDuct(self):
        rtn = ComplexDuct(self.name)
        rtn.parent = self.parent
        rtn.duct.inwards.cst_loss = self.duct1.inwards.cst_loss + self.duct2.inwards.cst_loss
        rtn.bleed.split_ratio = 1.

        self.update_connections(rtn)
        return rtn


class RealDuct(System):

    def setup(self):
        self.add_input(FluidPort, 'fl_in')
        self.add_output(FluidPort, 'fl_out')
        self.add_inward('glp', 0.05)
        self.add_outward('A', 1.)
        self.add_inward('PR', 1.)
        self.add_inward('ps', np.nan)
        self.add_inward('ts', np.nan)
        self.add_inward('v', np.nan)
        self.add_inward('rho', np.nan)
        self.add_inward('mach', 0.5)

    def compute(self):
        A = self.A
        gamma = 1.4
        r = 287.
        wr = self.fl_in.W * (self.fl_in.Tt) ** 0.5 / (self.fl_in.Pt * A)

        def wr_Mach(mach):
            return Residue.evaluate_residue(
                wr,
                mach * (1 + 0.5 * (gamma - 1) * mach ** 2) ** (0.5 * (gamma + 1) / (gamma - 1))
            )

        self.mach = root(wr_Mach, self.mach).x[0]
        logger.debug(f"Internal iterative, residue: {self.mach}, {wr_Mach(self.mach)}")
        f = (1 + 0.5 * (gamma - 1.) * self.mach ** 2)
        self.ps = self.fl_in.Pt / f ** (gamma / (gamma - 1.))
        self.ts = self.fl_in.Tt / f
        self.rho = self.ps / (r * self.ts)
        self.v = self.mach * (gamma * r * self.ts) ** 0.5
        loss = self.inwards.glp * 0.5 * self.rho * self.v ** 2
        self.fl_out.Pt = (1. - loss) * self.fl_in.Pt
        self.fl_out.W = self.fl_in.W
        self.fl_out.Tt = self.fl_in.Tt

        self.PR = self.fl_out.Pt / self.fl_in.Pt

    def Duct_to_ComplexDuct(self):
        rtn = ComplexDuct(self.name)
        rtn.parent = self.parent
        rtn.duct.inwards.cst_loss = self.inwards.cst_loss
        rtn.bleed.split_ratio = 1.

        self.plug_same(rtn)
        return rtn


class Splitter(System):

    def setup(self):
        self.add_input(FluidPort, 'fl_in')
        self.add_output(FluidPort, 'fl1_out')
        self.add_output(FluidPort, 'fl2_out')
        self.add_inward('split_ratio', 0.99)

    def compute(self):
        self.fl1_out.Pt = self.fl_in.Pt
        self.fl2_out.Pt = self.fl_in.Pt
        self.fl1_out.Tt = self.fl_in.Tt
        self.fl2_out.Tt = self.fl_in.Tt
        self.fl1_out.W = self.fl_in.W * self.split_ratio
        self.fl2_out.W = self.fl_in.W * (1 - self.split_ratio)


class Merger(System):

    def setup(self):
        self.add_input(FluidPort, 'fl1_in')
        self.add_input(FluidPort, 'fl2_in')
        self.add_output(FluidPort, 'fl_out')

    def compute(self):
        self.fl_out.Pt = self.fl1_in.Pt
        self.fl_out.Tt = self.fl1_in.Tt
        self.fl_out.W = self.fl1_in.W + self.fl2_in.W


class Atm(System):

    def setup(self):
        self.add_output(FluidState, 'fl_out', {'Pt': 101325, 'Tt': 273.15})
        self.add_inward('Pt', 101325)
        self.add_inward('Tt', 273.15)

    def compute(self):
        self.fl_out.Pt = self.inwards.Pt
        self.fl_out.Tt = self.inwards.Tt


class Inlet(System):

    def setup(self):
        self.add_input(FluidState, 'fl_in', {'Pt': 101325, 'Tt': 273.15})
        self.add_output(FluidPort, 'fl_out')
        self.add_input(FlowPort, 'W_in', variables={'W': 200})

        self.add_unknown("W_in.W")

    def compute(self):
        self.fl_out.Pt = self.fl_in.Pt * 0.995
        self.fl_out.Tt = self.fl_in.Tt
        self.fl_out.W = self.W_in.W


class Fan(System):

    def setup(self):
        self.add_input(FluidPort, 'fl_in')
        self.add_input(MechPort, 'mech_in')
        self.add_output(FluidPort, 'fl_out')

        self.add_inward('gh', 0.1)

        self.add_outward('pcnr', 0.)
        self.add_outward('pr', 0.)
        self.add_outward('effis', 1.)
        self.add_outward('wr', 0.)
        self.add_outward('PWfan', 1e6)

        self.add_unknown('gh')
        self.add_equation('fl_out.W == fl_in.W', 'Wfan')
        self.add_equation('PWfan == mech_in.PW', 'PWfan')

    def compute(self):
        fl_in = self.fl_in
        fl_out = self.fl_out

        if fl_in.Tt > 0:
            self.pcnr = self.mech_in.XN / (fl_in.Tt / 288.15) ** 0.5
            fl_out.W = 2 * (1 - self.gh) * self.pcnr / (fl_in.Tt / 288.15) ** 0.5 * (
                        fl_in.Pt / 101325.)
        else:
            logger.error(
                f"{self.name!r} at port 'fl_in': Tt cannot be negative or null")
            raise ZeroDivisionError

        fl_out.Pt = fl_in.Pt * (0.01 * (self.pcnr + self.gh) + 1)
        fl_out.Tt = fl_in.Tt * (fl_out.Pt / fl_in.Pt) ** (1 - 1 / 1.4)

        self.PWfan = fl_out.W * 1004 * (fl_out.Tt - fl_in.Tt)


class Nozzle(System):

    def setup(self):
        self.add_input(FluidPort, 'fl_in')
        self.add_inward('Acol', 0.4)
        self.add_inward('Aexit', 0.5)
        self.add_outward('WRnozzle')

        self.add_equation('WRnozzle == 241 * Acol')

    def compute(self):
        fl = self.fl_in
        self.WRnozzle = fl.W * (fl.Tt / 288.15) ** 0.5 / (fl.Pt / 101325)


class FanComplex(System):

    def setup(self):
        self.add_input(FluidPort, 'fl_in')
        self.add_output(FluidPort, 'fl_out')
        self.add_input(MechPort, 'mech_in')
        self.add_inward('gh', 0.1)

        self.add_child(ComplexDuct('ductC'))
        self.add_child(Fan('fan'))

        self.connect(self.fl_in, self.ductC.fl_in)
        self.connect(self.mech_in, self.fan.mech_in)
        self.connect(self.inwards, self.fan.inwards, 'gh')
        self.connect(self.ductC.fl_out, self.fan.fl_in)
        self.connect(self.fl_out, self.fan.fl_out)

        self.exec_order = ['ductC', 'fan']
                
        self.ductC.duct.inwards.cst_loss = 1.


class ComplexDuct(PlossFamily):

    def setup(self):
        self.add_input(FluidPort, 'fl_in')
        self.add_output(FluidPort, 'fl_out')

        self.add_child(Duct('duct'))
        self.add_child(Merger('merger'))
        self.add_child(Splitter(name='bleed'))

        self.connect(self.fl_in, self.merger.fl1_in)
        self.connect(self.fl_out, self.bleed.fl1_out)

        self.connect(self.merger.fl_out, self.duct.fl_in)
        self.connect(self.duct.fl_out, self.bleed.fl_in)
        self.connect(self.bleed.fl2_out, self.merger.fl2_in)

        self.exec_order = ['merger', 'duct', 'bleed']

    def ComplexDuct_to_Duct(self):
        rtn = Duct(self.name)
        rtn.parent = self.parent
        rtn.inwards.cst_loss = self.duct.inwards.cst_loss

        self.update_connections(rtn)
        return rtn

    def ComplexDuct_to_SerialDuct(self):
        rtn = SerialDuct(self.name)
        rtn.parent = self.parent
        rtn.duct1.inwards.cst_loss = self.duct.inwards.cst_loss / 2
        rtn.duct2.inwards.cst_loss = self.duct.inwards.cst_loss / 2

        self.update_connections(rtn)
        return rtn


class ComplexTurbofan(TurbofanFamily):

    def setup(self):
        self.add_child(Duct('duct'))
        self.add_child(Merger('merger'))
        self.add_child(Splitter(name='bleed'))
        self.add_child(Atm('atm'))
        self.add_child(Inlet('inlet'))
        self.add_child(Nozzle('noz'))
        self.add_child(FanComplex('fanC'))

        self.connect(self.inlet.fl_in, self.atm.fl_out)
        self.connect(self.fanC.fl_in, self.inlet.fl_out)
        self.connect(self.fanC.fl_out, self.merger.fl1_in)
        self.connect(self.bleed.fl2_out, self.merger.fl2_in)
        self.connect(self.merger.fl_out, self.duct.fl_in)
        self.connect(self.duct.fl_out, self.bleed.fl_in)
        self.connect(self.bleed.fl1_out, self.noz.fl_in)

        self.exec_order = ['atm', 'inlet', 'fanC', 'merger', 'duct', 'bleed', 'noz']

    def ComplexTurbofan_to_SimpleTurbofan(self):
        rtn = SimpleTurbofan(self.name)
        rtn.duct.cst_loss = 1.

        rtn.parent = self.parent
        self.update_connections(rtn)
        return rtn


class AdvancedTurbofan(TurbofanFamily):

    def setup(self):
        self.add_child(Duct('duct'))
        self.add_child(Merger('merger'))
        self.add_child(Splitter('bleed'))
        self.add_child(Atm('atm'))
        self.add_child(Inlet('inlet'))
        self.add_child(Nozzle('noz'))
        self.add_child(Fan('fan'))

        self.connect(self.inlet.fl_in, self.atm.fl_out)
        self.connect(self.fan.fl_in, self.inlet.fl_out)
        self.connect(self.fan.fl_out, self.merger.fl1_in)
        self.connect(self.bleed.fl2_out, self.merger.fl2_in)
        self.connect(self.merger.fl_out, self.duct.fl_in)
        self.connect(self.duct.fl_out, self.bleed.fl_in)
        self.connect(self.bleed.fl1_out, self.noz.fl_in)

        self.exec_order = ['atm', 'inlet', 'fan', 'merger', 'duct', 'bleed', 'noz']


class SimpleTurbofan(TurbofanFamily):

    def setup(self):
        self.add_child(Duct('duct'))
        self.add_child(Atm('atm'))
        self.add_child(Inlet('inlet'))
        self.add_child(Nozzle('noz'))
        self.add_child(Fan('fan'))

        self.connect(self.inlet.fl_in, self.atm.fl_out)
        self.connect(self.fan.fl_in, self.inlet.fl_out)
        self.connect(self.fan.fl_out, self.duct.fl_in)
        self.connect(self.duct.fl_out, self.noz.fl_in)

        self.exec_order = ['atm', 'inlet', 'fan', 'duct', 'noz']
