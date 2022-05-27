import enum
import itertools
import pathlib


class NounTypes(enum.Enum):
    """The various types of nouns supported by memorable."""

    ALCOHOLS = 'alcohols'
    ANIMALS = 'animals'
    CELESTIALS = 'celestials'
    DINOSAURS = 'dinosaurs'
    ELEMENTS = 'elements'
    FISH = 'fish'
    FOODS = 'foods'
    FRUITS = 'fruits'
    GEOGRAPHIES = 'geographies'
    HOUSEHOLDS = 'households'
    INVESTMENTS = 'investments'
    LITERATURE = 'literature'
    MYTHICAL = 'mythical'
    OCCUPATIONS = 'occupations'
    ORGANS = 'organs'
    PLACES = 'places'
    RELATIONS = 'relations'
    ROCKS = 'rocks'
    ROYALTY = 'royalty'
    TOOLS = 'tools'
    TRANSPORTS = 'transports'
    TREES = 'trees'
    VEGTABLES = 'vegtables'
    WATER_BODIES = 'water_bodies'


_PROJECT_DIR = pathlib.Path(__file__).parent
_RESOURCES_DIR = _PROJECT_DIR.joinpath('_resources')


def _load_resource(resource: str) -> list:
    """Load the given resource file"""
    return _RESOURCES_DIR.joinpath(
        f'{resource}.txt'
    ).read_text().strip().split('\n')


NAMES = _load_resource('names')
ADJECTIVES = _load_resource('adjectives')
ADVERBS = _load_resource('adverbs')
VERBS = _load_resource('verbs')

NOUN_MAP = {
    noun: _load_resource(f'nouns/{noun.value}') for noun in NounTypes
}

NOUNS = list(itertools.chain.from_iterable(NOUN_MAP.values()))
