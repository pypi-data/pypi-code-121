from .core import printHelp, getInput, inputVector

def inputGeometry(meshUnit):
    printHelp()
    geometry = {"comments" : {"meshUnit": meshUnit}}
    helpDoc = 'The Reference Area is used to non-dimensionalize ' \
              'lift coefficient (CL), drag coefficient (CD), force, '\
              'and moment coefficients.  For example,\n' \
              'CL = Lift / (1/2 * rho_inf * U_inf^2 * (Reference Area))\n' \
              'CD = Drag / (1/2 * rho_inf * U_inf^2 * (Reference Area))\n' \
              'CFx = (X Force) / (1/2 * rho_inf * U_inf^2 * (Reference Area))\n' \
              'CFy = (Y Force) / (1/2 * rho_inf * U_inf^2 * (Reference Area))\n' \
              'CFz = (Z Force) / (1/2 * rho_inf * U_inf^2 * (Reference Area))\n' \
              'Here rho_inf is the freestream density and ' \
              'U_inf is the freestream velocity.'
    geometry['refArea'] = getInput('Reference area (square {})'.format(meshUnit),
                                   helpDoc, float)
    print()
    helpDoc = 'The Moment Center used to calculate moments. ' \
              'All moments are calculated with respect to this moment center. '\
              'For example:\n' \
              'A z-directional force acting at an x-coordinate ' \
              'greater than the x-coordinate of the Moment Center would generate '\
              'a negative y-moment.\n' \
              'An x-directional force acting at an z-coordinate ' \
              'greater than the z-coordinate of the Moment Center would generate '\
              'a positive y-moment.\n' \
              'An x-directional force acting at an y-coordinate ' \
              'greater than the y-coordinate of the Moment Center would generate '\
              'a negative z-moment.\n' \
              'A y-directional force acting at an x-coordinate ' \
              'greater than the x-coordinate of the Moment Center would generate '\
              'a positive z-moment.\n' \
              'A y-directional force acting at an z-coordinate ' \
              'greater than the z-coordinate of the Moment Center would generate '\
              'a negative x-moment.\n' \
              'A z-directional force acting at an y-coordinate ' \
              'greater than the y-coordinate of the Moment Center would generate '\
              'a positive x-moment.'
    geometry['momentCenter'] = inputVector('Moment Center ({})'.format(meshUnit),
                                           helpDoc, [0,0,0])
    print()
    helpDoc = 'The Reference Length is used to non-dimensionalize ' \
              'moment coefficients.  For example,\n' \
              'CMx = My / (1/2 * rho_inf * U_inf^2 * (Reference Area) * (X Moment Length))\n' \
              'CMy = My / (1/2 * rho_inf * U_inf^2 * (Reference Area) * (Y Moment Length))\n' \
              'CMz = My / (1/2 * rho_inf * U_inf^2 * (Reference Area) * (Z Moment Length))\n' \
              'Here My is the Y-moment around the Moment Center, ' \
              'rho_inf is the freestream density and ' \
              'U_inf is the freestream velocity.'
    geometry['momentLength'] = inputVector('Moment Length ({})'.format(meshUnit), helpDoc)
    print()
    return geometry
