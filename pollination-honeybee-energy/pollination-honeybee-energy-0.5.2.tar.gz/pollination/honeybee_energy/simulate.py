from dataclasses import dataclass
from pollination_dsl.function import Inputs, Outputs, Function, command


@dataclass
class SimulateModel(Function):
    """Simulate a Model JSON file in EnergyPlus."""

    model = Inputs.file(
        description='An energy Model as either a HBJSON, OSM, or IDF.',
        path='model.hbjson',
        extensions=['hbjson', 'json', 'osm', 'idf']
    )

    epw = Inputs.file(
        description='Weather file.', path='weather.epw', extensions=['epw']
    )

    ddy = Inputs.file(
        description='Optional design day file to be used in the sizing calculation '
        'if no design days are specified in the sim_par.',
        path='weather.ddy', extensions=['ddy'], optional=True
    )

    sim_par = Inputs.file(
        description='SimulationParameter JSON that describes the settings for the '
        'simulation.', path='sim-par.json', extensions=['json'], optional=True
    )

    measures = Inputs.folder(
        description='A folder containing an OSW JSON be used as the base for the '
        'execution of the OpenStudio CLI. This folder must also contain all of the '
        'measures that are referenced within the OSW.', path='measures', optional=True
    )

    additional_string = Inputs.str(
        description='An additional text string to be appended to the IDF before '
        'simulation. The input should include complete EnergyPlus objects as a '
        'single string following the IDF format. This input can be used to include '
        'small EnergyPlus objects that are not currently supported by honeybee. '
        'Note that the additional-idf input should be used for larger objects '
        'that are too long to fit in a command.',
        default=''
    )

    additional_idf = Inputs.file(
        description='An IDF file with text to be appended before simulation. This '
        'input can be used to include large EnergyPlus objects that are not '
        'currently supported by honeybee.',
        path='additional.idf', extensions=['idf'], optional=True
    )

    report_units = Inputs.str(
        description='A switch to indicate whether the data in the output HTML report '
        'should be in SI or IP units. Valid values are "si" and "ip" and "none". '
        'If "none", no HTML report will be produced.', default='none',
        spec={'type': 'string', 'enum': ['none', 'si', 'ip']}
    )

    viz_variables = Inputs.str(
        description='Text for EnergyPlus output variables to be visualized on the '
        'geometry in an output view_data HTML report. If unspecified, no view_data '
        'report is produced. Each variable should be in "quotes" and should be '
        'preceded by a -v option. For example\n-v "Zone Air System Sensible Heating '
        'Rate" -v "Zone Air System Sensible Cooling Rate".', default=''
    )

    @command
    def simulate_model(self):
        return 'honeybee-energy simulate model model.hbjson weather.epw ' \
            '--sim-par-json sim-par.json --measures measures --additional-string ' \
            '"{{self.additional_string}}" --additional-idf additional.idf ' \
            '--report-units {{self.report_units}} --folder output {{self.viz_variables}}'

    result_folder = Outputs.folder(
        description='Folder containing all simulation result files.',
        path='output/run'
    )

    hbjson = Outputs.file(
        description='A clean version of the input model that is in a format, which can '
        'be easily consumed by OpenStudio and directly matched to EnergyPlus results.',
        path='output/in.hbjson', optional=True
    )

    osm = Outputs.file(
        description='The OpenStudio model used in the simulation.',
        path='output/run/in.osm', optional=True
    )

    idf = Outputs.file(
        description='The IDF model used in the simulation.',
        path='output/run/in.idf'
    )

    sql = Outputs.file(
        description='The result SQL file output by the simulation.',
        path='output/run/eplusout.sql'
    )

    zsz = Outputs.file(
        description='The result CSV with the zone loads over the design day output '
        'by the simulation.', path='output/run/epluszsz.csv', optional=True
    )

    html = Outputs.file(
        description='The result HTML page with summary reports output by the '
        'simulation.', path='output/run/eplustbl.htm'
    )

    err = Outputs.file(
        description='The error report output by the simulation.',
        path='output/run/eplusout.err'
    )

    result_report = Outputs.file(
        description='The HTML report with interactive summaries of energy use, '
        'HVAC component sizes, and other information.', optional=True,
        path='output/reports/openstudio_results_report.html'
    )

    visual_report = Outputs.file(
        description='The HTML report with hourly EnergyPlus output variables '
        'visualized on the geometry.', optional=True,
        path='output/reports/view_data_report.html'
    )


@dataclass
class SimulateModelRoomBypass(Function):
    """Simulate Model in EnergyPlus but with a check that prevents failure for no Rooms.
    """

    model = Inputs.file(
        description='An energy Model as a HBJSON.',
        path='model.hbjson',
        extensions=['hbjson', 'json']
    )

    epw = Inputs.file(
        description='Weather file.', path='weather.epw', extensions=['epw']
    )

    ddy = Inputs.file(
        description='Optional design day file to be used in the sizing calculation '
        'if no design days are specified in the sim_par.',
        path='weather.ddy', extensions=['ddy'], optional=True
    )

    sim_par = Inputs.file(
        description='SimulationParameter JSON that describes the settings for the '
        'simulation. If unspecified, some default parameters will be generated to '
        'request monthly energy usage.', path='sim-par.json', extensions=['json'],
        optional=True
    )

    measures = Inputs.folder(
        description='A folder containing an OSW JSON be used as the base for the '
        'execution of the OpenStudio CLI. This folder must also contain all of the '
        'measures that are referenced within the OSW.', path='measures', optional=True
    )

    additional_string = Inputs.str(
        description='An additional text string to be appended to the IDF before '
        'simulation. The input should include complete EnergyPlus objects as a '
        'single string following the IDF format. This input can be used to include '
        'small EnergyPlus objects that are not currently supported by honeybee. '
        'Note that the additional-idf input should be used for larger objects '
        'that are too long to fit in a command.',
        default=''
    )

    additional_idf = Inputs.file(
        description='An IDF file with text to be appended before simulation. This '
        'input can be used to include large EnergyPlus objects that are not '
        'currently supported by honeybee.',
        path='additional.idf', extensions=['idf'], optional=True
    )

    @command
    def simulate_model_room_check(self):
        return 'honeybee-energy simulate model model.hbjson weather.epw ' \
            '--sim-par-json sim-par.json --measures measures --additional-string ' \
            '"{{self.additional_string}}" --additional-idf additional.idf ' \
            '--check-model --skip-no-rooms --folder output'

    hbjson = Outputs.file(
        description='A clean version of the input model that is in a format, which can '
        'be easily consumed by OpenStudio and directly matched to EnergyPlus results.',
        path='output/in.hbjson', optional=True
    )

    osm = Outputs.file(
        description='The OpenStudio model used in the simulation.',
        path='output/run/in.osm', optional=True
    )

    idf = Outputs.file(
        description='The IDF model used in the simulation.',
        path='output/run/in.idf', optional=True
    )

    sql = Outputs.file(
        description='The result SQL file output by the simulation.',
        path='output/run/eplusout.sql', optional=True
    )

    zsz = Outputs.file(
        description='The result CSV with the zone loads over the design day output '
        'by the simulation.', path='output/run/epluszsz.csv', optional=True
    )

    html = Outputs.file(
        description='The result HTML page with summary reports output by the '
        'simulation.', path='output/run/eplustbl.htm', optional=True
    )

    err = Outputs.file(
        description='The error report output by the simulation.',
        path='output/run/eplusout.err', optional=True
    )


@dataclass
class SimulateOsm(Function):
    """Simulate an OSM file in EnergyPlus."""

    osm = Inputs.file(
        description='Path to a simulate-able OSM file.', path='model.osm',
        extensions=['osm']
    )

    epw = Inputs.file(
        description='Weather file.', path='weather.epw', extensions=['epw']
    )

    @command
    def simulate_model(self):
        return 'honeybee-energy simulate osm model.osm weather.epw --folder output'

    idf = Outputs.file(
        description='The IDF model used in the simulation.',
        path='output/run/in.idf'
    )

    sql = Outputs.file(
        description='The result SQL file output by the simulation.',
        path='output/run/eplusout.sql'
    )

    zsz = Outputs.file(
        description='The result CSV with the zone loads over the design day output '
        'by the simulation.', path='output/run/epluszsz.csv', optional=True
    )

    html = Outputs.file(
        description='The result HTML page with summary reports output by the '
        'simulation.', path='output/run/eplustbl.htm'
    )

    err = Outputs.file(
        description='The error report output by the simulation.',
        path='output/run/eplusout.err'
    )


@dataclass
class SimulateIdf(Function):
    """Simulate an IDF file in EnergyPlus."""

    idf = Inputs.file(
        description='Path to a simulate-able IDF file.', path='model.idf',
        extensions=['idf']
    )

    epw = Inputs.file(
        description='Weather file.', path='weather.epw', extensions=['epw']
    )

    @command
    def simulate_model(self):
        return 'honeybee-energy simulate idf model.idf weather.epw --folder output'

    output_folder = Outputs.folder(
        description='The output folder that includes all of the files generated by the '
        'simulation.', path='output'
    )

    sql = Outputs.file(
        description='The result SQL file output by the simulation.',
        path='output/eplusout.sql', optional=True
    )

    zsz = Outputs.file(
        description='The result CSV with the zone loads over the design day output '
        'by the simulation.', path='output/epluszsz.csv', optional=True
    )

    html = Outputs.file(
        description='The result HTML page with summary reports output by the '
        'simulation.', path='output/eplustbl.htm', optional=True
    )

    err = Outputs.file(
        description='The error report output by the simulation.',
        path='output/eplusout.err'
    )
