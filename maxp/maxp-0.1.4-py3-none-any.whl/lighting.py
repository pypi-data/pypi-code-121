from .. import rt
from . import fileio

LIGHT_DOME_NAME = "_Dome"
LIGHT_ACCENT_BACK_NAME = "_AccentBack"
LIGHT_ACCENT_SIDE_NAME = "_AccentSide"


def importLightRig() -> bool:
    print("importing...")
    rigFile = fileio.relative("..\\resources\\LightRig.max")
    print(rigFile)
    rt.mergeMaxFile(rigFile)  # MAXScript
    return True


def doesRigExist() -> bool:
    results = []
    for name in [LIGHT_DOME_NAME, LIGHT_ACCENT_BACK_NAME, LIGHT_ACCENT_SIDE_NAME]:
        node = rt.getNodeFromName(name)
        if node is None:
            results.append(False)
            continue
        results.append(True)
    return False if False in results else True
