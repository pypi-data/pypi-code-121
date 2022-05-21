"""Bot's configuration."""
from dataclasses import dataclass, field
from typing import Optional, Dict, Set, Mapping

from .misc import Properties
from .substitutions import Substitutions


@dataclass
class BotConfig:
    """
    Dataclass that contains all configuration files of the bot.

    The only missing is its knowledge (which is saved in the graphmaster).
    """

    # substitutions
    normalize = Substitutions()
    """Substitutions used with <normalize> tag."""
    denormalize = Substitutions()
    """Substitutions used with <denormalize> tag."""
    gender = Substitutions()
    """Substitutions used with <gender> tag."""
    person = Substitutions()
    """Substitutions used with <person> tag."""
    person2 = Substitutions()
    """Substitutions used with <person2> tag."""

    properties = Properties()
    """Bot properties."""

    default_predicate = "unknown"
    """Default value of the _predicate.

    When no _predicate with corresponding name is found in `session.predicates`
    or in `self.predicate_defaults`, this is the value that will be used.
    """

    default_answer = "I have no answer for that."
    """Reply returned when the interpretation fails."""

    predicate_defaults: Dict[str, str] = field(default_factory=dict)
    """Default values for the predicates.

    If during the evaluation, <get name="_predicate"> is called and
    there is no _predicate in current user session with this name,
    the value from this dict will be used.
    """

    sets: Dict[str, Set[str]] = field(default_factory=dict)
    """Mapping from set name to the set - AIML 2.x sets.

    Bot's sets, used to evaluate pattern-side <set>. Is is enough
    to load them after the .aiml files, as the parsing and storing
    to graphmaster does not require the sets to exist.
    """

    maps: Dict[str, Mapping[str, str]] = field(default_factory=dict)
    """Mapping from map name to the map - AIML 2.x maps.

    Bot's maps. Used at the evaluation of <map> tag. As the argument
    of dictionary has type mapping, it is enough to provide
    an object inheriting from `collections.abs.Mapping`, e.g.
    see implementation of standard maps in /stdlib/.
    """

    # aiml 1.x feature, deprecated in AIML 2.x
    gossip_filename: Optional[str] = None
    """Absolute path to file where to store <gossip/>.

    If no path is provided, the contents of <gossip> are discarded,
    as this tag produces no output. The file be be created, if not
    exists at the first encounter of <gossip> tag.
    """

    # aiml 2.0 feature
    learnf_file: str = "./learnf.aiml"
    """Path to file where to store <learnf/>.

    This file, if not exists, will be created at the first encounter
    of <learnf/> tag during evaluation.
    """
