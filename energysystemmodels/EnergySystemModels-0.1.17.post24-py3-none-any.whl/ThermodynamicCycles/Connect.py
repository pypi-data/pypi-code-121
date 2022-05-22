from ThermodynamicCycles.FluidPort.FluidPort import FluidPort
def Fluid_connect( a=FluidPort(),b=FluidPort()):
    a.fluid=b.fluid
    a.P=b.P
    a.h=b.h
    a.F_kgs=b.F_kgs
    return "connectés"