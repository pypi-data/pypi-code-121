from pathlib import Path

PATH = Path(__file__).parent.absolute()

ICON = PATH / "assets" / "icon.png"
BG =  PATH / "assets" / "background.png"
B_BG = PATH / "assets" / "Empty_Node.png"

__all__ = ["BG","ICON"]