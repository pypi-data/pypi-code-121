
#
# Import section
#
import numpy

from syned.beamline.beamline_element import BeamlineElement
from syned.beamline.element_coordinates import ElementCoordinates
from wofry.propagator.propagator import PropagationManager, PropagationElements, PropagationParameters

from wofry.propagator.wavefront2D.generic_wavefront import GenericWavefront2D

from wofryimpl.propagator.propagators2D.fresnel_zoom_xy import FresnelZoomXY2D
from wofryimpl.propagator.propagators2D.fresnel import Fresnel2D
from wofryimpl.propagator.propagators2D.fresnel_convolution import FresnelConvolution2D
from wofryimpl.propagator.propagators2D.fraunhofer import Fraunhofer2D
from wofryimpl.propagator.propagators2D.integral import Integral2D
from wofryimpl.propagator.propagators2D.fresnel_zoom_xy import FresnelZoomXY2D

from srxraylib.plot.gol import plot, plot_image
plot_from_oe = 100 # set to a large number to avoid plots


##########  SOURCE ##########


#
# create output_wavefront
#
#
output_wavefront = GenericWavefront2D.initialize_wavefront_from_range(x_min=-0.00012,x_max=0.00012,y_min=-5e-05,y_max=5e-05,number_of_points=(400,200))
output_wavefront.set_photon_energy(7000)
output_wavefront.set_gaussian_hermite_mode(sigma_x=3.00818e-05,sigma_y=6.99408e-06,amplitude=1,nx=0,ny=0,betax=0.129748,betay=1.01172)


if plot_from_oe <= 0: plot_image(output_wavefront.get_intensity(),output_wavefront.get_coordinate_x(),output_wavefront.get_coordinate_y(),aspect='auto',title='SOURCE')


##########  OPTICAL SYSTEM ##########





##########  OPTICAL ELEMENT NUMBER 1 ##########



input_wavefront = output_wavefront.duplicate()
from wofryimpl.beamline.optical_elements.ideal_elements.screen import WOScreen

optical_element = WOScreen()

# drift_before 36 m
#
# propagating
#
#
propagation_elements = PropagationElements()
beamline_element = BeamlineElement(optical_element=optical_element,    coordinates=ElementCoordinates(p=36.000000,    q=0.000000,    angle_radial=numpy.radians(0.000000),    angle_azimuthal=numpy.radians(0.000000)))
propagation_elements.add_beamline_element(beamline_element)
propagation_parameters = PropagationParameters(wavefront=input_wavefront,    propagation_elements = propagation_elements)
#self.set_additional_parameters(propagation_parameters)
#
propagation_parameters.set_additional_parameters('shift_half_pixel', 1)
propagation_parameters.set_additional_parameters('magnification_x', 8.0)
propagation_parameters.set_additional_parameters('magnification_y', 10.0)
#
propagator = PropagationManager.Instance()
try:
    propagator.add_propagator(FresnelZoomXY2D())
except:
    pass
output_wavefront = propagator.do_propagation(propagation_parameters=propagation_parameters,    handler_name='FRESNEL_ZOOM_XY_2D')


#
#---- plots -----
#
if plot_from_oe <= 1: plot_image(output_wavefront.get_intensity(),output_wavefront.get_coordinate_x(),output_wavefront.get_coordinate_y(),aspect='auto',title='OPTICAL ELEMENT NR 1')


##########  OPTICAL ELEMENT NUMBER 2 ##########



input_wavefront = output_wavefront.duplicate()
from syned.beamline.shape import Rectangle
boundary_shape=Rectangle(-2.015e-05, 2.015e-05, -0.0001135, 0.0001135)
from wofryimpl.beamline.optical_elements.absorbers.slit import WOSlit
optical_element = WOSlit(boundary_shape=boundary_shape)

# no drift in this element
output_wavefront = optical_element.applyOpticalElement(input_wavefront)


#
#---- plots -----
#
if plot_from_oe <= 2: plot_image(output_wavefront.get_intensity(),output_wavefront.get_coordinate_x(),output_wavefront.get_coordinate_y(),aspect='auto',title='OPTICAL ELEMENT NR 2')


##########  OPTICAL ELEMENT NUMBER 3 ##########



input_wavefront = output_wavefront.duplicate()
from wofryimpl.beamline.optical_elements.ideal_elements.screen import WOScreen

optical_element = WOScreen()

# drift_before 29 m
#
# propagating
#
#
propagation_elements = PropagationElements()
beamline_element = BeamlineElement(optical_element=optical_element,    coordinates=ElementCoordinates(p=29.000000,    q=0.000000,    angle_radial=numpy.radians(0.000000),    angle_azimuthal=numpy.radians(0.000000)))
propagation_elements.add_beamline_element(beamline_element)
propagation_parameters = PropagationParameters(wavefront=input_wavefront,    propagation_elements = propagation_elements)
#self.set_additional_parameters(propagation_parameters)
#
propagation_parameters.set_additional_parameters('shift_half_pixel', 1)
propagation_parameters.set_additional_parameters('magnification_x', 2.5)
propagation_parameters.set_additional_parameters('magnification_y', 1.0)
#
propagator = PropagationManager.Instance()
try:
    propagator.add_propagator(FresnelZoomXY2D())
except:
    pass
output_wavefront = propagator.do_propagation(propagation_parameters=propagation_parameters,    handler_name='FRESNEL_ZOOM_XY_2D')


#
#---- plots -----
#
if plot_from_oe <= 3: plot_image(output_wavefront.get_intensity(),output_wavefront.get_coordinate_x(),output_wavefront.get_coordinate_y(),aspect='auto',title='OPTICAL ELEMENT NR 3')


##########  OPTICAL ELEMENT NUMBER 4 ##########



input_wavefront = output_wavefront.duplicate()
from orangecontrib.esrf.wofry.util.lens import WOLens

optical_element = WOLens.create_from_keywords(
    name='Real Lens 2D',
    number_of_curved_surfaces=2,
    two_d_lens=1, # 0=2D  1=TANGENTIAL 2=SAGITTAL
    surface_shape=0,
    wall_thickness=5e-05,
    material='Be',
    lens_radius=0.0002094,
    n_lenses=1,
    aperture_shape=1, # 0=circular, 1=rect
    aperture_dimension_h=0.001,
    aperture_dimension_v=0.001)

# no drift in this element

print("_foc_plane, _shape, _apert_h, _apert_v, _r_min, _n, _wall_thickness, _aperture", optical_element.get_barc_inputs())
output_wavefront = optical_element.applyOpticalElement(input_wavefront)
#
#
# #
# #---- plots -----
# #
# if plot_from_oe <= 4: plot_image(output_wavefront.get_intensity(),output_wavefront.get_coordinate_x(),output_wavefront.get_coordinate_y(),aspect='auto',title='OPTICAL ELEMENT NR 4')