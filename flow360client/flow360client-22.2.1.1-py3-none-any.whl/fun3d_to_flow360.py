import sys
import json

def process_nml(nml):
    groups = {}
    for line in nml.splitlines():
        line = line.strip()
        if '!' in line:
            line = line.split('!')[0].strip()

        if line == '':
            continue
        elif line.startswith('&'):
            group_key = line[1:]
            group = {}
        elif line == '/':
            groups[group_key] = group
            del group
            del group_key
        elif 'case_title' in line:
            continue
        else:
            key, value = [a.strip() for a in line.split('=')]
            group[key.strip()] = value.strip()
    return groups

def translate_freestream(g):
    assert eval(g['temperature_units']) == 'Kelvin'
    mach_number = g.get('mach_number')
    freestream = {
        'Reynolds' : float(g['reynolds_number']),
        'Temperature' : float(g['temperature']),
        'alphaAngle' : float(g['angle_of_attack']),
        'betaAngle' : float(g['angle_of_yaw'])
    }
    if mach_number is not None:
        freestream['Mach'] = float(mach_number)
    return freestream

def translate_geometry(g):
    return {
        "refArea" : float(g['area_reference']),
        "momentCenter" : [float(g['x_moment_center']),
                          float(g['y_moment_center']),
                          float(g['z_moment_center'])],
        "momentLength" : [float(g['y_moment_length']),
                          float(g['x_moment_length']),
                          float(g['y_moment_length'])]
    }

def translate_navier_stokes(rc, nl, **args):
    params = args
    CFL = {}
    for key, value in nl.items():
        if key.find('schedule_iteration') != -1:
            CFL['rampSteps'] = int(value.split()[1].strip()) - int(value.split()[0].strip(','))
        if key.find('schedule_cfl') != -1 and key.find('schedule_cflturb') == -1:
            CFL['initial'] = float(value.split()[0].strip(','))
            CFL['final'] = float(value.split()[1])

    args.update({"maxSteps" : int(rc['steps'])})
    if CFL:
        args.update({
            "CFL" : CFL
        });
    return args

def translate_turbulence(nl, **args):
    params = args
    CFL = {}
    for key, value in nl.items():
        if key.find('schedule_iteration') != -1:
            CFL['rampSteps'] = int(value.split()[1]) - int(value.split()[0].strip(','))
        if key.find('schedule_cflturb') != -1:
            CFL['initial'] = float(value.split()[0].strip(','))
            CFL['final'] = float(value.split()[1])
    if CFL:
        args.update({
            "CFL" : CFL
        });
    return args

def translate_inviscid_flux(rc, invf, **args):
    if invf:
        foi = invf.get('first_order_iterations')
        if foi:
            args.update({'firstOrderIterations' : int(foi)})

    args.update({"maxSteps" : int(rc['steps'])})

    return args

def translate_nml(nml):
    dc = {}
    if nml.get('reference_physical_properties'):
        dc['freestream'] = translate_freestream(nml['reference_physical_properties'])

    if nml.get('force_moment_integ_properties'):
        dc['geometry'] = translate_geometry(nml['force_moment_integ_properties'])

    if nml.get('nonlinear_solver_parameters'):
        dc['navierStokesSolver'] = translate_navier_stokes(nml['code_run_control'],
                                                           nml['nonlinear_solver_parameters'])
        dc['turbulenceModelSolver'] = translate_turbulence(nml['nonlinear_solver_parameters'],
                                                           modelType='SpalartAllmaras')

#    dc['runControl'] = translate_inviscid_flux(nml['code_run_control'], nml.get('inviscid_flux_method'))
    return dc

def translate_boundaries(mapbc):
    mapbc = mapbc.strip().splitlines()
    num_bc = int(mapbc[0].strip())
    mapbc = mapbc[1:]
    assert len(mapbc) == num_bc
    bc = {}
    bc_map = {
        '3000': "SlipWall",
        '4000': "NoSlipWall",
        '5000': "Freestream",
        '5050': "Freestream",
        '5051' : "SubsonicOutflowPressure",
        '5052' : "SubsonicOutflowMach",
        '6662': "SlipWall",
        '7011' : "SubsonicInflow",
        '7012' : "SubsonicOutflowPressure",
        '7031' : "MassOutflow",
        '7036' : "MassInflow"
    }
    noslipWalls = []
    for line in mapbc:
        bc_num, bc_type, bc_name = [i.strip() for i in line.split()]
        bc[bc_num] = {
            "type" : bc_map[bc_type],
            "name" : bc_name
        }
        if int(bc_type) == 4000:
            noslipWalls.append(int(bc_num))
    return bc, noslipWalls


if __name__ == "__main__":
    try:
        try:
            fun3d_nml = open(sys.argv[1]).read()
        except Exception as e:
            print('Could not read fun3d.nml file {0}!'.format(sys.argv[1]))
            raise
        try:
            mapbc = open(sys.argv[2]).read()
        except Exception as e:
            print('Could not read .mapbc file {0}!'.format(sys.argv[2]))
            raise
        dest = sys.argv[3]
        if dest.endswith('.json') != True:
            print('Destination file must end with .json!')
            raise RuntimeError('InvalidExtension')
    except:
        print("Error. Usage: python3 fun3d_to_flow360.py fun3d.nml CASE_NAME.mapbc dest/Flow360.json")
        sys.exit(-1)
    bc, noslipWalls = translate_boundaries(mapbc)
    nml = process_nml(fun3d_nml)
    flow360_json = translate_nml(nml)
    flow360_json['boundaries'] = bc
    json.dump(flow360_json, open(dest,'w+'), indent=4, sort_keys=True)
