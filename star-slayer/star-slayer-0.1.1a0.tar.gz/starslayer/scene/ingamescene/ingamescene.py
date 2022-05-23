"""
In-Game Scene.
"""

from ...consts import GUI_SPACE, HEIGHT, WIDTH, PLAYER_HEALTH_BAR_ANIM
from ...graphics.animations import SinusoidalWave
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

        aux_cons = (HEIGHT / 70)
        aux_cons_2 = (HEIGHT / 175)
        bar_start = WIDTH - GUI_SPACE + aux_cons
        bar_end = WIDTH - aux_cons

        self.add_animation(SinusoidalWave(x1=bar_start + aux_cons_2,
                                          y1=(HEIGHT * 0.9) + aux_cons_2,
                                          x2=bar_end,
                                          y2=(HEIGHT - aux_cons - aux_cons_2),
                                          vertical=False,
                                          dot_density=45.0,
                                          dot_radius=2.5,
                                          wave_speed=1.5,
                                          bulge_frequency=8,
                                          fill_name="HEALTH_COLOR_2",
                                          outline_name=''),
                           name=f"{PLAYER_HEALTH_BAR_ANIM}_1",
                           is_front=True)
        self.add_animation(SinusoidalWave(x1=bar_start + aux_cons_2,
                                          y1=(HEIGHT * 0.9) + aux_cons_2,
                                          x2=bar_end,
                                          y2=(HEIGHT - aux_cons - aux_cons_2),
                                          vertical=False,
                                          initial_phase=20.0,
                                          dot_density=45.0,
                                          dot_radius=2.5,
                                          wave_speed=1.5,
                                          bulge_frequency=8,
                                          fill_name="HEALTH_COLOR_2",
                                          outline_name=''),
                           name=f"{PLAYER_HEALTH_BAR_ANIM}_2",
                           is_front=True)
        self.add_animation(SinusoidalWave(x1=bar_start + aux_cons_2,
                                          y1=(HEIGHT * 0.9) + aux_cons_2,
                                          x2=bar_end,
                                          y2=(HEIGHT - aux_cons - aux_cons_2),
                                          vertical=False,
                                          dot_density=40.0,
                                          dot_radius=2.5,
                                          wave_speed=3.5,
                                          translation_speed=60.0,
                                          bulge_frequency=4,
                                          fill_name="HEALTH_COLOR_2",
                                          outline_name=''),
                           name=f"{PLAYER_HEALTH_BAR_ANIM}_3",
                           is_front=True)
