from dataclasses import dataclass
from pollination_dsl.function import Inputs, Outputs, Function, command


@dataclass
class ModelToOsm(Function):
    """Translate a Model JSON file into an OpenStudio Model and corresponding IDF."""

    model = Inputs.file(
        description='Honeybee model in JSON format.', path='model.json',
        extensions=['hbjson', 'json']
    )

    sim_par = Inputs.file(
        description='SimulationParameter JSON that describes the settings for the '
        'simulation.', path='sim-par.json', extensions=['json']
    )

    @command
    def model_to_osm(self):
        return 'honeybee-energy translate model-to-osm model.json ' \
            '--sim-par-json sim-par.json --folder output ' \
            '--log-file output/output_paths.json'

    osm = Outputs.file(
        description='The OpenStudio model file.', path='output/run/in.osm'
    )

    idf = Outputs.file(
        description='The IDF file.', path='output/run/in.idf'
    )


@dataclass
class ModelOccSchedules(Function):
    """Translate a Model's occupancy schedules into a JSON of 0/1 values.

    This JSON is useful in workflows that compute thermal comfort percent,
    daylight autonomy, etc.
    """

    model = Inputs.file(
        description='Honeybee model in JSON or Pkl format.', path='model.json',
        extensions=['hbjson', 'json', 'hbpkl', 'pkl']
    )

    period = Inputs.str(
        description='An AnalysisPeriod string to dictate the start and end of the '
        'exported occupancy values (eg. "6/21 to 9/21 between 0 and 23 @1"). Note '
        'that the timestep of the period will determine the timestep of output '
        'values. If unspecified, the values will be annual.', default=''
    )

    threshold = Inputs.float(
        description='A number between 0 and 1 for the threshold at and above which '
        'a schedule value is considered occupied.', default=0.1,
        spec={'type': 'number', 'maximum': 1, 'minimum': 0}
    )

    @command
    def export_model_occ_schedules(self):
        return 'honeybee-energy translate model-occ-schedules model.json ' \
            '--threshold {{self.threshold}} --period "{{self.period}}" ' \
            '--output-file occ_schedules.json'

    occ_schedule_json = Outputs.file(
        description='An occupancy schedule JSON that is useful in workflows like '
        'thermal comfort percent, daylight autonomy, etc.', path='occ_schedules.json'
    )


@dataclass
class ModelTransSchedules(Function):
    """Translate Model shade transmittance schedules into a JSON of fractional values.
    """

    model = Inputs.file(
        description='Honeybee model in JSON or Pkl format.', path='model.json',
        extensions=['hbjson', 'json', 'hbpkl', 'pkl']
    )

    period = Inputs.str(
        description='An AnalysisPeriod string to dictate the start and end of the '
        'exported values (eg. "6/21 to 9/21 between 0 and 23 @1"). Note '
        'that the timestep of the period will determine the timestep of output '
        'values. If unspecified, the values will be annual.', default=''
    )

    @command
    def export_model_trans_schedules(self):
        return 'honeybee-energy translate model-transmittance-schedules model.json ' \
            '--period "{{self.period}}" --output-file trans_schedules.json'

    trans_schedule_json = Outputs.file(
        description='A schedule JSON that contains fractional schedule values '
        'for each shade transmittance schedule in the model', path='trans_schedules.json'
    )
