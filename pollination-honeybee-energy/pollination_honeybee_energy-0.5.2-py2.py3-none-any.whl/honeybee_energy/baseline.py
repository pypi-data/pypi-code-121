from dataclasses import dataclass
from pollination_dsl.function import Inputs, Outputs, Function, command


@dataclass
class Geometry2004(Function):
    """Convert a Model's geometry to conform to ASHRAE 90.1-2004 appendix G.

    This includes stripping out all attached shades (leaving detached shade as
    context), reducing the vertical glazing ratio to 40% it it's above this value,
    and reducing the skylight ratio to 5% of it's above this value.
    """

    model = Inputs.file(
        description='Honeybee model in JSON format.', path='model.hbjson',
        extensions=['hbjson', 'json']
    )

    @command
    def geometry_2004(self):
        return 'honeybee-energy baseline geometry-2004 model.hbjson ' \
            '--output-file new_model.hbjson'

    new_model = Outputs.file(
        description='Model JSON with its properties edited to conform to ASHRAE '
        '90.1 appendix G.', path='new_model.hbjson'
    )


@dataclass
class Constructions2004(Function):
    """Convert a Model's constructions to conform to ASHRAE 90.1-2004 appendix G.

    This includes assigning a ConstructionSet that is compliant with Table 5.5 to
    all rooms in the model.
    """

    model = Inputs.file(
        description='Honeybee model in JSON format.', path='model.hbjson',
        extensions=['hbjson', 'json']
    )

    climate_zone = Inputs.str(
        description='Text indicating the ASHRAE climate zone. This can be a single '
        'integer (in which case it is interpreted as A) or it can include the '
        'A, B, or C qualifier (eg. 3C).',
        spec={
            'type': 'string',
            'enum': [
                '1', '2', '3', '4', '5', '6', '7', '8',
                '1A', '2A', '3A', '4A', '5A', '6A', '7A', '8A',
                '1B', '2B', '3B', '4B', '5B', '6B', '7B', '8B',
                '3C', '4C', '5C'
            ]
        }
    )

    @command
    def constructions_2004(self):
        return 'honeybee-energy baseline constructions-2004 model.hbjson ' \
            '{{self.climate_zone}} --output-file new_model.hbjson'

    new_model = Outputs.file(
        description='Model JSON with its properties edited to conform to ASHRAE '
        '90.1 appendix G.', path='new_model.hbjson'
    )


@dataclass
class Lighting2004(Function):
    """Convert a Model's lighting to conform to ASHRAE 90.1-2004 appendix G.

    This includes determining whether an ASHRAE 2004 equivalent exists for each
    program type in the model. If none is found, the baseline_watts_per_area on
    the room's program's lighting will be used, which will default to a typical
    office if none has been specified.
    """

    model = Inputs.file(
        description='Honeybee model in JSON format.', path='model.hbjson',
        extensions=['hbjson', 'json']
    )

    @command
    def lighting_2004(self):
        return 'honeybee-energy baseline lighting-2004 model.hbjson ' \
            '--output-file new_model.hbjson'

    new_model = Outputs.file(
        description='Model JSON with its properties edited to conform to ASHRAE '
        '90.1 appendix G.', path='new_model.hbjson'
    )


@dataclass
class Hvac2004(Function):
    """Convert a Model's HVAC to conform to ASHRAE 90.1-2004 appendix G.

    This includes the selection of the correct Appendix G template HVAC based on
    the inputs and the application of this HVAC to all conditioned spaces in
    the model.
    """

    model = Inputs.file(
        description='Honeybee model in JSON format.', path='model.hbjson',
        extensions=['hbjson', 'json']
    )

    climate_zone = Inputs.str(
        description='Text indicating the ASHRAE climate zone. This can be a single '
        'integer (in which case it is interpreted as A) or it can include the '
        'A, B, or C qualifier (eg. 3C).',
        spec={
            'type': 'string',
            'enum': [
                '1', '2', '3', '4', '5', '6', '7', '8',
                '1A', '2A', '3A', '4A', '5A', '6A', '7A', '8A',
                '1B', '2B', '3B', '4B', '5B', '6B', '7B', '8B',
                '3C', '4C', '5C'
            ]
        }
    )

    is_residential = Inputs.str(
        description='A switch to note whether the model represents a residential '
        'or nonresidential building.', default='nonresidential',
        spec={'type': 'string', 'enum': ['nonresidential', 'residential']}
    )

    energy_source = Inputs.str(
        description='A switch to note whether the available energy source is '
        'fossil fuel based or all-electric.', default='fuel',
        spec={'type': 'string', 'enum': ['fuel', 'electric']}
    )

    floor_area = Inputs.float(
        description='A number for the floor area of the building that the model '
        'is a part of in m2. If 0, the model floor area will be used.', default=0
    )

    story_count = Inputs.int(
        description='An integer for the number of stories of the building that the '
        'model is a part of. If None, the model stories will be used.', default=0,
        spec={'type': 'integer', 'minimum': 0}
    )

    @command
    def hvac_2004(self):
        return 'honeybee-energy baseline hvac-2004 model.hbjson {{self.climate_zone}} ' \
            '--{{self.is_residential}} --{{self.energy_source}} ' \
            '--story-count {{self.story_count}} --floor-area {{self.floor_area}} ' \
            '--output-file new_model.hbjson'

    new_model = Outputs.file(
        description='Model JSON with its properties edited to conform to ASHRAE '
        '90.1 appendix G.', path='new_model.hbjson'
    )


@dataclass
class RemoveEcms(Function):
    """Remove energy conservation strategies (ECMs) not associated with baseline models.

    This includes removing the opening behavior of all operable windows, daylight
    controls, etc.
    """

    model = Inputs.file(
        description='Honeybee model in JSON format.', path='model.hbjson',
        extensions=['hbjson', 'json']
    )

    @command
    def remove_ecms(self):
        return 'honeybee-energy baseline remove-ecms model.hbjson ' \
            '--output-file new_model.hbjson'

    new_model = Outputs.file(
        description='Model JSON with its properties edited to conform to ASHRAE '
        '90.1 appendix G.', path='new_model.hbjson'
    )
