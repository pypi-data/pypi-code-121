from dataclasses import dataclass


@dataclass(frozen=True)
class Location:
    story_quests: dict = None


@dataclass(frozen=True)
class ChampsInfo:
    json: dict = None
    name: str = None
    mcoc_class: str = None
    tags: list = None
    contact: str = None
    tier: int = None
    rank: int = None
    challenger_rating: int = None
    prestige: int = None
    health: int = None
    attack: int = None
    abilities: dict = None
    crit_rate: int = None
    crit_damage: int = None
    armor: int = None
    block_proficiency: int = None
    energy_resistence: int = None
    physical_resistence: int = None
    crit_resistence: int = None
    signature_info: str = None
    location: Location = None
    url_page: str = None
    img_link: str = None
    status: int = None


def champ_checker(fancy_name: str):
    """
    Used to get correct champname
    MCOC Version: 35.0
    """
    champs_dict = {
        "ABOMINATION": "abomination",
        "IMMORTAL ABOMINATION": "ibom",
        "AEGON": "aegon",
        "AGENT VENOM": "agentvenom",
        "AIR WALKER": "airwalker",
        "AMERICA CHAVEZ": "americachavez",
        "ANGELA": "angela",
        "ANNIHILUS": "annihilus",
        "ANT MAN": "antman",
        "ANTI VENOM": "antivenom",
        "APOCALYPSE": "apocalypse",
        "ARCHANGEL": "archangel",
        "BEAST": "beast",
        "BISHOP": "bishop",
        "BLACK BOLT": "blackbolt",
        "BLACK CAT": "blackcat",
        "BLACK PANTHER OG": "blackpanther",
        "BLACK PANTHER CIVIL WAR": "bpcw",
        "BLACK WIDOW OG": "blackwidow",
        "BLACK WIDOW CLAIRE VOYANT": "bwcv",
        "BLACK WIDOW DEADLY ORIGIN": "bwdo",
        "BLADE": "blade",
        "CABLE": "cable",
        "CAPTAIN AMERICA": "captainamerica",
        "CAPTAIN AMERICA CIVIL WAR": "caiw",
        "CAPTAIN AMERICA(SAM WILSON)": "casw",
        "CAPTAIN AMERICA WW2": "caww2",
        "CAPTAIN BRITAIN": "captainbritain",
        "CAPTAIN MARVEL MOVIE": "cmm",
        "CAPTAIN MARVEL OG": "captainmarvel",
        "CARNAGE": "carnage",
        "CIVIL WARRIOR": "civilwarrior",
        "COLOSSUS": "colossus",
        "CORVUS GLAVE": "corvusglaive",
        "COSMIC GHOST RIDER": "cgr",
        "CROSSBONES": "crossbones",
        "CULL OBSIDIAN": "cullobsidian",
        "CYCLOPS(BLUE TEAM)": "cyclops_blue",
        "CYCLOPS (NEW XAVIER SCHOOL)": "cyclops",
        "DAREDEVIL": "daredevil",
        "DAREDEVIL NETFLIX": "daredevil_netflix",
        "DARKHAWK": "darkhawk",
        "DEADPOOL": "deadpool",
        "DEADPOOL X-FORCE": "deadpool_xforce",
        "DIABLO": "diablo",
        "DOCTOR DOOM": "doctordoom",
        "DOCTOR OCTOPUS": "docock",
        "DR. STRANGE": "drstrange",
        "DOCTOR VOODOO": "doctorvoodoo",
        "DOMINO": "domino",
        "DORMAMMU": "dormammu",
        "DRAGON MAN": "dragonman",
        "DRAX": "drax",
        "EBONY MAW": "ebonymaw",
        "ELECTRO": "electro",
        "ELEKTRA": "elektra",
        "ELSA BLOODSTONE": "elsabloodstone",
        "EMMA FROST": "emmafrost",
        "FALCON": "falcon",
        "GAMBIT": "gambit",
        "GAMORA": "gamora",
        "GHOST": "ghost",
        "GHOST RIDER": "ghostrider",
        "GOLDPOOL": "goldpool",
        "GREEN GOBLIN": "greengoblin",
        "GROOT": "groot",
        "GUARDIAN": "guardian",
        "GUILLOTINE": "guillotine",
        "GUILLOTINE 2099": "guillotine_2099",
        "GWENPOOL": "gwenpool",
        "HAVOK": "havok",
        "HAWKEYE": "hawkeye",
        "HEIMDALL": "heimdall",
        "HELA": "hela",
        "HERCULES": "hercules",
        "HIT MONKEY": "hitmonkey",
        "HOWARD THE DUCK": "howard",
        "HULK": "hulk",
        "IMMORTAL HULK": "hulk_immortal",
        "HULK RAGNAROK": "hulk_ragnarok",
        "HULKBUSTER": "hulkbuster_movie",
        "HUMAN TORCH": "humantorch",
        "HYPERION": "hyperion",
        "ICEMAN": "iceman",
        "IKARIS": "ikaris",
        "INVISIBLE WOMEN": "invisiblewoman",
        "IRON FIST": "ironfist",
        "IRON FIST IMMORTAL": "ironfistimmortal",
        "IRON MAN OG": "ironman",
        "IRON MAN INFINITY WAR": "imiw",
        "IRON PATRIOT": "ironpatriot",
        "JABARI PANTHER": "jabaripanther",
        "JOE FIXIT": "joefixit",
        "JUBILEE": "jubilee",
        "JUGGERNAUT": "juggernaut",
        "KANG": "kang",
        "KARNAK": "karnak",
        "KILLMONGER": "killmonger",
        "KING GROOT": "kinggroot",
        "KINGPIN": "kingpin",
        "KITTY PRYDE": "kittypryde",
        "KNULL": "knull",
        "KORG": "korg",
        "KRAVEN": "kraven",
        "LOKI": "loki",
        "LONGSHOT": "longshot",
        "LUKECAGE": "lukecage",
        "MODOK": "modok",
        "MAGIK": "magik",
        "MAGNETO": "magneto",
        "MAGNETO (HOUSE OF X)": "magnetowhite",
        "MAN-THING": "manthing",
        "MANGOG": "mangog",
        "MASACRE": "masacre",
        "MEDUSA": "medusa",
        "MEPHISTO": "mephisto",
        "MISTER FANTASTIC": "misterfantastic",
        "MISETER NEGATIVE": "misternegative",
        "MISTER SINISTER": "mistersinister",
        "MISTY KNIGHT": "mistyknight",
        "MOJO": "mojo",
        "MOLE-MAN": "moleman",
        "MOONKNIGHT": "moonknight",
        "MORDO": "mordo",
        "MORNINGSTAR": "morningstar",
        "MS. MARVEL": "msmarvel",
        "MS. MARVEL (KAMALA KHAN)": "msmarvel_kamala",
        "MYSTERIO": "mysterio",
        "NAMOR": "namor",
        "NEBULA": "nebula",
        "NICK FURY": "nickfury",
        "NIGHT THRASHER": "nightthrasher",
        "NIGHT CRAWLER": "nightcrawler",
        "NIMROD": "nimrod",
        "NOVA": "nova",
        "ODIN": "odin",
        "OLD MAN LOGAN": "oml",
        "OMEGA RED": "omegared",
        "OMEGA SENTINEL": "omegasentinel",
        "PENI PARKER": "peniparker",
        "PHOENIX": "phoenix",
        "PLATINUMPOOL": "platinumpool",
        "PROFESSOR X": "professorx",
        "PROXIMA MIDNIGHT": "proximamidnight",
        "PSYCHOMAN": "psychoman",
        "PSYLOCKE": "psylocke",
        "PUNISHER": "punisher",
        "PUNISHER 2099": "punisher2099",
        "PURGATORY": "purgatory",
        "QUAKE": "quake",
        "RED GOBLIN": "red_goblin",
        "RED GUARDIAN": "redguardian",
        "RED HULK": "hulk_red",
        "RED SKULL": "redskull",
        "RHINO": "rhino",
        "RHINTRAH": "rhintrah",
        "ROCKET": "rocket",
        "ROGUE": "rogue",
        "RONAN": "ronan",
        "RONIN": "ronin",
        "SABRETOOTH": "sabretooth",
        "SASQUATCH": "sasquatch",
        "SAURON": "sauron",
        "SCARLET WITCH SIGIL": "scarletwitchnew",
        "SCARLET WITCH OG": "scarletwitch",
        "SCORPION": "scorpion",
        "SENTINEL": "sentinel",
        "SENTRY": "sentry",
        "SERSI": "sersi",
        "SHANG CHI": "shangchi",
        "SHE-HULK": "shehulk",
        "SIVER CENTURION": "silvercenturion",
        "SILVER SURFER": "silversurfer",
        "SORCERER SUPREME": "sorcerersupreme",
        "SPIDER GWEN": "spidergwen",
        "SPIDER HAM": "spiderham",
        "SPIDER MAN": "spiderman",
        "SPIDER MAN MILES MORALES": "spidermorales",
        "SPIDER MAN STARK ENHANCED": "starkspiderman",
        "SPIDER MAN STEALTH": "spiderstealth",
        "SPIDER MAN SYMBIOTE": "spidersymbiote",
        "SPIDER MAN 2099": "spiderman2099",
        "SQUIRREL GIRL": "squirrelgirl",
        "STAR LORD": "starlord",
        "STORM": "storm",
        "STORM PYRAMID X": "stormpyramidx",
        "STRYFE": "stryfe",
        "SUNSPOT": "sunspot",
        "SUPER SKRULL": "superskrull",
        "SUPERIOR IRON MAN": "superiorironman",
        "SYMBIOTE SUPREME": "symbiotesupreme",
        "TASKMASTER": "taskmaster",
        "TERRAX": "terrax",
        "THANOS": "thanos",
        "THE CHAMPION": "champion",
        "THE HOOD": "hood",
        "OVERSEER": "overseer",
        "THING": "thing",
        "THOR": "thor",
        "THOR JANE FOSTER": "janefoster",
        "THOR RAGNAROK": "thorragnarok",
        "TIGRA": "tigra",
        "TOAD": "toad",
        "ULTRON(LOL)": "ultronlol",
        "ULTRON": "ultron",
        "UNSTOPPABLE COLOSSUS": "unstoppablecolossus",
        "VENOM": "venom",
        "VENOM THE DUCK": "venomtheduck",
        "VENOMPOOL": "venompool",
        "VISION OG": "vision",
        "VISION AARKUS": "visionaarkus",
        "VISION (AGE OF ULTRON)": "visionmovie",
        "VOID": "void",
        "VULTURE": "vulture",
        "WAR MACHINE": "warmachine",
        "WARLOCK": "warlock",
        "WASP": "wasp",
        "WINTER SOLDIER": "wintersoldier",
        "WOLVERINE": "wolverine",
        "WOLVERINE WEAPON-X": "wolverinex",
        "WONG": "wong",
        "X-23": "x23",
        "YELLOW JACKET": "yellowjacket",
        "YONDU": "yondu",
    }

    try:
        return champs_dict[fancy_name]
    except:
        return fancy_name


@dataclass(frozen=True)
class NodeInfo:
    json: dict = None
    id: int = None
    name: str = None
    info: str = None
    status: int = None


@dataclass(frozen=True)
class RosterDict:
    champ_name: str = None
    tier: int = None
    rank: int = None
    prestige: int = None
    sig_number: int = None
    img_link: str = None
    url_page: str = None


@dataclass(frozen=True)
class Roster:
    json: dict = None
    discord_id: int = None
    gamename: str = None
    avatar_url: str = None
    prestige: int = None
    about_me: str = None
    roster: list[RosterDict] = None
