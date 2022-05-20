"""
In-Game Scene.
"""

from ..scene import Scene


class InGameScene(Scene):
    """
    In-Game Scene. Contains the gameplay
    part of the game.
    """

    def __init__(self, name_id: str="scene-in-game", **kwargs) -> None:
        """
        Initializes an instance of 'InGameScene'.
        """

        super().__init__(name_id, **kwargs)
