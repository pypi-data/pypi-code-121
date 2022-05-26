from cosapp.systems import System
from cosapp.ports import Port
from cosapp.tests.library.ports import XPort


class FloatPort(Port):
    def setup(self):
        self.add_variable('x', 1.0)

class Eq_2u_1(System):
    def setup(self):
        self.add_inward('u')
        self.add_unknown('u').add_equation(('10.*u == 1.'))


class Sys_Sum3_1Eq_2Mult(System):
    def setup(self):
        self.add_input(XPort, 'x_in')
        self.add_input(XPort, 'u_in')
        self.add_child(XportMultiplier("Mult_by_2_1", factor=2))
        self.add_child(XportMultiplier("Mult_by_2_2", factor=2), pulling = {"x_out":"x_out"})
        self.add_child(Eq_2u_1("Eq2u1"))
        self.add_output(XPort, 'u_out')

        self.connect(self.Mult_by_2_1.x_in, self.x_in)
        self.connect(self.Mult_by_2_2.x_in, self.Mult_by_2_1.x_out)
    def compute(self):
        self.x_out.x = self.x_out.x + 3
        self.u_out.x = self.x_out.x + self.u_in.x


class XPort_2D_Provider(System):
    def setup(self):
        self.add_output(XPort, 'x_out')
        self.add_output(XPort, 'u_out')
    def compute(self):
        self.x_out.x = 2.5
        self.u_out.x = 1.5


class Sys_Provider_1Eq_2Mult_Getter(System):
    def setup(self):
        self.add_child(XPort_2D_Provider('Provider'))
        self.add_child(Sys_Sum3_1Eq_2Mult('Eq_2Mult'))
        self.add_child(XPort_2D_Getter('Get2D'))

        #A CO-IN
        self.connect(self.Eq_2Mult.x_in, self.Provider.x_out)
        self.connect(self.Eq_2Mult.u_in, self.Provider.u_out)
        
        #F CO-IN
        self.connect(self.Get2D.x_in, self.Eq_2Mult.x_out)
        self.connect(self.Get2D.u_in, self.Eq_2Mult.u_out)


class XPort_2D_Getter(System):
    def setup(self):
        self.add_input(XPort, 'x_in')
        self.add_input(XPort, 'u_in')
        self.add_output(XPort, 'x_out')
        self.add_output(XPort, 'u_out')

    def compute(self):
        self.x_out.x = self.x_in.x
        self.u_out.x = self.u_in.x


class XportMultiplier(System):
    def setup(self, factor=2):
        self.add_property('factor', factor)
        self.add_input(XPort, 'x_in')
        self.add_output(XPort, 'x_out')

    def compute(self):
        self.x_out.x = self.factor * self.x_in.x


class Sys_Mult_XPort_Inward(System):

    def setup(self):
        self.add_input(XPort, 'm', {'x': 1})
        self.add_input(XPort, 'x_in')
        self.add_output(XPort, 'x_out')
    
        self.add_unknown('m.x')
    
    def compute(self):
        self.x_out.x = self.m.x * self.x_in.x


class XPort_2D_Getter_E(System):

    def setup(self):
        self.add_input(XPort, 'x_in')
        self.add_input(XPort, 'u_in')
        self.add_output(XPort, 'x_out')
        self.add_output(XPort, 'u_out')

        self.add_equation('x_out.x == 110')

    def compute(self):
        self.x_out.x = self.x_in.x
        self.u_out.x = self.u_in.x
        

class Sys_P_MI_1E2M_1U_G(System):
    def setup(self):
        #INPUTS
        self.add_input(XPort, 'x_in')
        self.add_input(XPort, 'u_in')
        
        #OUTPUTS
        self.add_output(XPort, 'x_out')
        self.add_output(XPort, 'u_out')

        #CHILDREN
        self.add_child(Sys_Mult_XPort_Inward('SMXI'))
        self.add_child(XPort_2D_Getter('Get2D'))
        self.add_child(Sys_Sum3_1Eq_2Mult('S1E2M'))

        #SMXI CO-IN
        self.connect(self.SMXI.x_in, self.x_in)
        
        #S1E2M CO-IN
        self.connect(self.S1E2M.u_in, self.u_in)
        self.connect(self.S1E2M.x_in, self.SMXI.x_out)
        
        #GET2D CO-IN
        self.connect(self.Get2D.x_in, self.S1E2M.x_out)
        self.connect(self.Get2D.u_in, self.S1E2M.u_out)

        #SELF CO-OUT
        self.connect(self.x_out, self.Get2D.x_out)
        self.connect(self.u_out, self.Get2D.u_out)

        self.exec_order = ['SMXI', 'S1E2M', 'Get2D']


class Sys_PME2MUG_G_1E(System):
    def setup(self):
        self.add_child(Sys_P_MI_1E2M_1U_G('PMEMUG'))
        self.add_child(XPort_2D_Getter_E('G2DEq'))

        #G2DEq CO-IN
        self.connect(self.G2DEq.x_in, self.PMEMUG.x_out)
        self.connect(self.G2DEq.u_in, self.PMEMUG.u_out)


class Sys_Unknown(System):
    def setup(self):
        self.add_input(XPort, 'u_in')
        self.add_input(XPort, 'x_in')
        self.add_unknown('x_in.x')
        self.add_output(XPort, 'u_out')
        self.add_output(XPort, 'x_out')
    
    def compute(self):
        self.u_out.x = self.u_in.x
        self.x_out.x = self.x_in.x


class Sys_Basic_Eq(System):
    def setup(self):
        self.add_input(XPort, 'x_in')
        self.add_equation('x_in.x == 25')


class Sys_Sum3_2Eq_2Mult(System):

    def setup(self):
        self.add_input(XPort, 'x_in')
        self.add_input(XPort, 'u_in')

        self.add_output(XPort, 'u_out')

        self.add_child(XportMultiplier("Mult_by_2_1", factor=2), pulling="x_in")
        self.add_child(XportMultiplier("Mult_by_2_2", factor=2), pulling="x_out")
        self.add_child(Eq_2u_1("Eq2u1"))
        self.add_child(Sys_Basic_Eq('Basic_Eq'))

        self.connect(self.Mult_by_2_2.x_in, self.Mult_by_2_1.x_out)
        self.connect(self.Basic_Eq.x_in, self.Mult_by_2_1.x_out)
    
    def compute(self):
        self.x_out.x += 3
        self.u_out.x = self.x_out.x + self.u_in.x


class Sys_Unknown_1Eq_2Mult_Getter(System):
    def setup(self):
        self.add_child(Sys_Unknown('Provider'))
        self.add_child(Sys_Sum3_2Eq_2Mult('Eq_2Mult'))
        self.add_child(XPort_2D_Getter('Get2D'))

        #A CO-IN
        self.connect(self.Eq_2Mult.x_in, self.Provider.x_out)
        self.connect(self.Eq_2Mult.u_in, self.Provider.u_out)
        
        #F CO-IN
        self.connect(self.Get2D.x_in, self.Eq_2Mult.x_out)
        self.connect(self.Get2D.u_in, self.Eq_2Mult.u_out)


class Sys_Double_Integrate(System):
    
    def setup(self):
        self.add_input(FloatPort, 'a_in')
        self.add_inward('v0', 0.1)
        self.add_inward('h0', 0.1)
        
        self.add_output(FloatPort, 'h_out')

        self.add_transient('v', der='a_in.x')
        self.add_transient('h', der='v')

    def compute(self):
        self.h_out.x = self.h


class FloatPortDivider(System):
    
    def setup(self, factor):
        self.add_property('factor', factor)
        self.add_input(FloatPort, 'h_in')
        self.add_output(FloatPort, 'h_out')
    
    def compute(self):
        self.h_out.x = self.h_in.x / self.factor


class Sys_DivBy2(System):

    def setup(self):
        self.add_input(FloatPort, 'h_in')
        self.add_output(FloatPort, 'a_out')
    
    def compute(self):
        self.a_out.x = self.h_in.x / 2.


class Sys_DivBy2_DoubleInt(System):

    def setup(self):
        self.add_child(Sys_DivBy2('ln_div'), pulling='h_in')
        self.add_child(Sys_Double_Integrate('DI'), pulling='h_out')

        self.connect(self.DI.a_in, self.ln_div.a_out)


class Sys_Looped_Div_Int_Div(System):

    def setup(self):
        self.add_child(XportMultiplier("Mult", factor=2))
        self.add_child(Sys_DivBy2_DoubleInt("DLDI"))
        self.add_child(FloatPortDivider("Divider", factor=10))
        
        self.connect(self.DLDI.h_in, self.Mult.x_out)
        self.connect(self.Divider.h_in, self.DLDI.h_out)
        self.connect(self.Mult.x_in, self.Divider.h_out)
