from sympy import symbols, integrate
from sympy.functions.elementary.piecewise import Piecewise
from sympy.functions import Abs
from scipy import constants as const

h = symbols('altitude')

# https://en.wikipedia.org/w/index.php?title=Density_of_air&oldid=862508599#Altitude
standard_values = {
    'standard_sea_level_pressure': const.atm,
    'standard_sea_level_temperature': const.zero_Celsius,#+15.0,
    'earth_surface_gravitational_acceleration': const.g,
    'universal_gas_constant': const.R,
    'molar_mass_of_dry_air': const.physical_constants[
        'molar volume of ideal gas (273.15 K, 101.325 kPa)'][0],
    #0.0289644 # Kg/mol at sea, 15'C.
}

p0, T0, g, R, M = symbols(','.join(standard_values.keys()))

# Temperature Lapse rates
L_atmosphere = Piecewise(
    (0.0065, h <=11000),  # troposphere
    (0, h <=20000),       # tropopause
    (-0.0017, h <=50000), # stratosphere
    (0, h <=55000),       # stratopause
    (0.00375, h <=80000), # mesosphere
    (0, h <=90000),       # mesopause
    (-0.0048, h<=527343), # thermosphere to point where it is 2000'C.
    (0, h > 527343)       # -exosphere-
)

# http://www.physicalgeography.net/fundamentals/7b.html
T_atmospehre = T0.subs(standard_values) - integrate(L_atmosphere)

# https://en.wikipedia.org/w/index.php?title=Barometric_formula&oldid=838719040#Pressure_equations
# P_atmosphere = Piecewise(
#     (1, L_atmosphere == 0),
#     (2, L_atmosphere != 0)
# )
# D_atmosphere = (P_atmosphere*M)/(R*T_atmospehre)
