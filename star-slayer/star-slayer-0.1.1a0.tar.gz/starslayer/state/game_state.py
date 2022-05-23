"""
Logics Module. Its purpose is to control the logic behaviour
of the game.
"""

from importlib import import_module
from os import listdir
from random import choice, randrange
from typing import TYPE_CHECKING, Dict, List, Optional

from ..consts import (EXITING_DELAY, GUI_SPACE, HEIGHT, HOOKS_GROUPS_PATH,
                      KEYS_PATH, PLAYER_HEALTH_BAR_ANIM, PROFILES_PATH, WIDTH)
from ..enemies import EnemyCommonA, EnemyCommonB
from ..files import (ProfilesDict, StrDict, list_actions, list_profiles,
                     list_repeated_keys, load_json)
from ..hooks import HooksGroup
from ..logger import GameLogger
from ..power_levels import SimplePower
from ..scene import (CharacterScene, ControlScene, InGameScene, MainScene,
                     OptionScene, ProfileScene, Scene, SceneDict)
from ..selector import ColorSelector
from ..utils import Chronometer, HitBox, HitCircle, Menu, Timer

if TYPE_CHECKING:

    from ..bullets import Bullet
    from ..characters import PlayableCharacter
    from ..enemies import Enemy
    from ..entity import Entity
    from ..power_levels import PowerLevel
    from ..utils import BoundingShape

CornersTuple = tuple[int | float, int | float, int | float, int | float]
TimerDict = Dict[str, Timer]
ChronDict = Dict[str, Chronometer]
EventsDict = Dict[str, bool]
BulletsList = List["Bullet"]


class Game:
    """
    Class for the Game itself.
    """

    def __init__(self) -> None:
        """
        Initalizes an instance of type 'Game'.
        """

        # Level Parameters
        self.game_level: int = 1
        self.score: int = 0

        # Player Parameters
        self.player: Optional["PlayableCharacter"] = None
        self.power_level: "PowerLevel" = SimplePower()
        self.player_bullets: BulletsList = []

        # Color Profiles
        self.color_profiles: ProfilesDict = load_json(PROFILES_PATH)
        self._color_theme: List[str] = list_profiles(self.color_profiles)[0]
        self.color_profile: StrDict = self.color_profiles[self._color_theme]

        # Sub-menu related
        self.action_to_show: str = list_actions(load_json(KEYS_PATH))[0]
        self.sub_menu: Optional[Menu] = None

        # Timers
        self.timers: TimerDict = {"debug_cooldown": Timer(20)}
        self.special_timers: TimerDict = {"exiting_cooldown": Timer(EXITING_DELAY)}
        self.chronometers: ChronDict = {"level_time": Chronometer()}

        # Enemies
        self.enemies: List["Enemy"] = []
        self.enemies_bullets: BulletsList = []

        # Control Attributes
        self.control_attributes: Dict[str, bool] = {}
        self.control_attributes.update(is_on_prompt=False,
                                       show_debug_info=False,
                                       show_about=False,
                                       exiting=False,
                                       exit=False)

        # Selector
        self.color_selector = self.generate_color_selector()
        self.attribute_to_edit: Optional[str] = None

        # Actions
        self.__hooks_groups: List[HooksGroup] = []
        self.load_hook_groups()

        # Scenes
        self.scenes: SceneDict = {}
        self.current_scene: Optional[Scene] = None
        self.load_scenes()


        # events control
        self.keys_pressed: EventsDict = {}
        self.keys_released: EventsDict = {}
        self.events_processed: EventsDict = {}
        self.time_flow: int = 60 # fps


    @staticmethod
    def process_key(key: str) -> str:
        """
        Reads which key was pressed, and returns its corresponding action.
        The key is guaranteed to already exist it the json file.
        """

        return load_json(KEYS_PATH).get(key)


    def apply_events(self,
                     key: str,
                     events_dict: EventsDict,
                     action: str,
                     original_action: str) -> None:
        """
        Updates the events dictionaries to match the current events.
        """

        if events_dict.get(key, False):

            self.events_processed[action] = True

        elif all((not events_dict.get(repeated_key, False)
                 for repeated_key in list_repeated_keys(original_action,
                                                        load_json(KEYS_PATH)))):

            self.events_processed[action] = False


    def process_events(self) -> None:
        """
        Processes all the events currently happening.
        """

        for key in self.keys_pressed:

            action = self.process_key(key)
            self.apply_events(key, self.keys_pressed, action, action)

        for key_r in self.keys_released:

            original_action = self.process_key(key_r)
            action = f"{original_action}_RELEASE"
            self.apply_events(key_r, self.keys_released, action, original_action)
            self.keys_released[key_r] = False # Release events should be done only once

        for game_action in self.events_processed:
            if self.events_processed.get(game_action, False):
                self.execute_action(game_action)


    def add_group(self, new_group: HooksGroup) -> None:
        """
        Adds new group to internal actions groups list.
        """

        self.__hooks_groups.append(new_group)


    def delete_group(self, group: HooksGroup) -> Optional[HooksGroup]:
        """
        Deletes an action group.
        If it finds it, it returns such group.
        """

        group_to_return = None

        if group in self.__hooks_groups:

            group_to_return = group
            self.__hooks_groups.remove(group)

        return group_to_return


    def load_hook_groups(self) -> None:
        """
        Loads all the hook groups located in the `starlsayer.hooks.groups` package.
        """

        for file_name in listdir(HOOKS_GROUPS_PATH):
            if file_name.startswith("__"):
                continue

            module = import_module(f"..hooks.groups.{file_name.removesuffix('.py')}",
                                   "starslayer.state")
            module.setup_hook(self)


    def add_scene(self, new_scene: Scene) -> None:
        """
        Adds a new scene to the game.
        """

        if not self.current_scene:
            self.current_scene = new_scene

        self.scenes[new_scene.id] = new_scene
        new_scene.resfresh_sub_menus(self) # One initial refresh


    def remove_scene(self, scene: Scene) -> Optional[Scene]:
        """
        Removes and returns a scene of the game, if available.
        """

        if self.current_scene == scene:
            self.current_scene = None

        return self.scenes.pop(scene.id, None)


    def change_scene(self, scene_id: str) -> None:
        """
        Searches for a scene name id. If it finds it,
        the current scene is replaced.
        """

        scene = self.scenes.get(scene_id, None)

        if scene:
            self.current_scene.reset_hook()
            self.current_scene = scene


    def load_scenes(self) -> None:
        """
        Loads the scenes into the game.
        """

        mainscene = MainScene()
        optionscene = OptionScene(parent=mainscene)
        controlscene = ControlScene(parent=optionscene)
        profilescene = ProfileScene(parent=optionscene)
        characterscene = CharacterScene(parent=mainscene)
        ingamescene = InGameScene(parent=mainscene)

        self.add_scene(mainscene)
        self.add_scene(optionscene)
        self.add_scene(controlscene)
        self.add_scene(profilescene)
        self.add_scene(characterscene)
        self.add_scene(ingamescene)


    def start_game(self) -> None:
        """
        Formally starts the game.
        """

        if not self.player:
            self.log.error(f"Player {self.player!r} is not a valid playable character.")
            return

        self.change_scene("scene-in-game")


    def execute_action(self, action: str) -> None:
        """
        Executes one specified action.
        """

        for group in self.__hooks_groups:
            group.execute_act(action)


    # pylint: disable=invalid-name
    def execute_button(self, x: int, y: int, **kwargs) -> None:
        """
        Tries to execute a button handler.
        """

        if self.current_scene and self.current_scene.execute_button(self, x, y, **kwargs):
            # There should be only one button in all of the
            # scenes that coincides with these coords
            return


    @property
    def log(self) -> GameLogger:
        """
        Returns the game logger.
        """

        return GameLogger()


    @property
    def is_in_game(self) -> bool:
        """
        Checks if the game is the playable area or not.
        """

        return self.current_scene == self.scenes.get("scene-in-game", "-= not-in-game =-")


    @property
    def debug_cooldown(self) -> Timer:
        """
        Returns the cooldown for showing debug messages.
        """

        return self.timers.get("debug_cooldown")


    @property
    def level_time(self) -> Chronometer:
        """
        Returns the time of the current level.
        """

        return self.chronometers.get("level_time")


    @property
    def exiting_cooldown(self) -> Timer:
        """
        Returns the timer fot exiting the game.
        """

        return self.special_timers.get("exiting_cooldown")


    @property
    def is_on_prompt(self) -> bool:
        """
        Returns the control boolean `is_on_prompt`.
        """

        return self.control_attributes.get("is_on_prompt")


    @is_on_prompt.setter
    def is_on_prompt(self, new_value: bool) -> None:
        """
        Changes the value for the control boolean `is_on_prompt`.
        """

        self.control_attributes["is_on_prompt"] = new_value


    @property
    def show_debug_info(self) -> bool:
        """
        Returns the control boolean `show_debug_info`.
        """

        return self.control_attributes.get("show_debug_info")


    @show_debug_info.setter
    def show_debug_info(self, new_value: bool) -> None:
        """
        Changes the value for the control boolean `show_debug_info`.
        """

        self.control_attributes["show_debug_info"] = new_value


    @property
    def show_about(self) -> bool:
        """
        Returns the control boolean `show_about`.
        """

        return self.control_attributes.get("show_about")


    @show_about.setter
    def show_about(self, new_value: bool) -> None:
        """
        Changes the value for the control boolean `show_about`.
        """

        self.control_attributes["show_about"] = new_value


    @property
    def exiting(self) -> bool:
        """
        Returns the control boolean `exiting`.
        """

        return self.control_attributes.get("exiting")


    @exiting.setter
    def exiting(self, new_value: bool) -> None:
        """
        Changes the value for the control boolean `exiting`.
        """

        self.control_attributes["exiting"] = new_value


    @property
    def exit(self) -> bool:
        """
        Returns the control boolean `exit`.
        """

        return self.control_attributes.get("exit")


    @exit.setter
    def exit(self, new_value: bool) -> None:
        """
        Changes the value for the control boolean `exit`.
        """

        self.control_attributes["exit"] = new_value


    @property
    def selected_theme(self) -> str:
        """
        Returns the current color theme (name only).
        """

        return self._color_theme


    @selected_theme.setter
    def selected_theme(self, new_value: str) -> None:
        """
        If the selected theme changes, then the profile should also do it.
        """

        real_name = '_'.join(new_value.upper().split())

        if real_name in self.color_profiles:

            self._color_theme = real_name
            self.color_profile = self.color_profiles[real_name]


    @property
    def all_bullets(self) -> BulletsList:
        """
        Returns all the bullets of the game.
        """

        return self.player_bullets + self.enemies_bullets


    def check_scene(self, name_id: str) -> bool:
        """
        Checks if a given scene is present in the game and is the
        current one showing.
        """

        return (name_id in self.scenes) and (self.current_scene == self.scenes[name_id])


    def go_prompt(self) -> None:
        """
        Sets the 'is_on_prompt' attribute to 'True' so that the
        next iteration, the program prompts the user for interaction.
        """

        self.is_on_prompt = True


    def prompt(self, *args, **kwargs) -> None:
        """
        Processes the action to prompt the user.
        """

        kwargs.update(game=self)
        self.current_scene.prompt(*args, **kwargs)


    def generate_color_selector(self) -> ColorSelector:
        """
        Generates and assigns the color selector of the game.
        """

        aux_x = (WIDTH // 75)
        aux_y = (HEIGHT // 70)

        area_x1, area_y1, area_x2, area_y2 = ((WIDTH // 15),
                                              (HEIGHT * 0.065714),
                                              (WIDTH * 0.866666),
                                              (HEIGHT * 0.928571))
        palette_corners = (area_x1 + aux_x,
                           area_y1 + aux_y,
                           area_x2 - aux_x,
                           area_y1 + ((area_y2 - area_y1) / 2))
        color_selector: ColorSelector = ColorSelector(area=(area_x1, area_y1, area_x2, area_y2),
                                                      palette_area=palette_corners,
                                                      rows=20, cols=30)

        return color_selector


    def level_up(self, how_much: int=1) -> None:
        """
        Increments by 'how_much' the level of the game.
        """

        self.game_level += how_much


    def power_up(self) -> None:
        """
        Increments by 'how_much' the power of the player.
        """

        next_level = self.power_level.next_level()
        if next_level:
            self.power_level = next_level

        self.player.change_cooldown(self.power_level.cooldown)
        self.player.change_invulnerability(self.power_level.invulnerability)


    def shoot_bullets(self) -> None:
        """
        Shoots bullets from player.
        """

        self.power_level.shoot_bullets(self.player, self.player_bullets)


    def check_shape_pos_and_entity_health(self,
                                          entity: "Entity",
                                          container: List["Entity"]) -> None:
        """
        Checks if an entity should disappear from the screen.
        """

        if any((entity.is_over(-(HEIGHT * 0.15)),
                entity.is_below(HEIGHT * 1.15),
                entity.has_no_health())):
            try:
                container.remove(entity)
            except ValueError:
                pass


    def _check_collision_type(self,
                              threat: "BoundingShape",
                              defender: "BoundingShape") -> bool:
        """
        Checks which type of collision to test with another entity.
        """

        if isinstance(threat, HitBox):
            return defender.collides_with_box(threat)
        if isinstance(threat, HitCircle):
            return defender.collides_with_circle(threat)


    def check_damage_to_player(self, threat: "Entity") -> None:
        """
        Checks a collision of a threat with the player.
        """

        if all((self._check_collision_type(threat, self.player),
                self.player.invulnerability.is_zero_or_less())):
            self.player.take_damage(threat.hardness)
            self.player.invulnerability.reset()

            for health_bar_anim in self.current_scene.\
                                   find_animation_match(fr"^{PLAYER_HEALTH_BAR_ANIM}_[0-9]+$"):
                health_bar_anim.change_crop(self.player.health_percentage())


    def check_damage_to_shield(self, threat: "Entity", threat_container: List["Entity"]) -> None:
        """
        Checks a collision of a threat with the player's shield.
        """

        shield = self.player.shield
        if not shield:
            return

        if self._check_collision_type(threat, shield):
            shield.take_damage(threat.hardness)
            threat.take_damage(shield.hardness)

        self.check_shape_pos_and_entity_health(threat, threat_container)


    def exec_player_bul_trajectory(self) -> None:
        """
        Moves each player bullet according to their trajectory.
        Player bullets do not actually hurt the player.
        """

        for player_bullet in self.player_bullets:
            player_bullet.trajectory()

            for threat in self.enemies + self.enemies_bullets:
                if self._check_collision_type(threat, player_bullet):
                    threat.take_damage(player_bullet.hardness)

                    if not player_bullet.is_ethereal:
                        player_bullet.take_damage(threat.hardness)

                    break

            self.check_shape_pos_and_entity_health(player_bullet, self.player_bullets)


    def exec_enem_trajectory(self) -> None:
        """
        Moves each enemy according to its defined behaviour.
        """

        for enem in self.enemies:
            enem.trajectory()
            self.check_damage_to_shield(enem, self.enemies)
            self.check_damage_to_player(enem)
            self.check_shape_pos_and_entity_health(enem, self.enemies)
            enem.shoot(self.enemies_bullets)


    def exec_enem_bul_trajectory(self) -> None:
        """
        Moves each player bullet according to their trajectory.
        These ones are the ones that do ouchie-ouchie.
        """

        for enem_bullet in self.enemies_bullets:
            enem_bullet.trajectory()
            self.check_damage_to_shield(enem_bullet, self.enemies_bullets)
            self.check_damage_to_player(enem_bullet)
            self.check_shape_pos_and_entity_health(enem_bullet, self.enemies_bullets)


    def spawn_enemies(self,
                      *,
                      when: int | float,
                      enemy_types: List["Enemy"],
                      amount_from: int=1,
                      amount_until: int=1,
                      spacing_x: int=20,
                      spacing_y: int=5
                      ) -> None:
        """
        Given the parameters, effectively spawns the enemies on the game.
        """

        if float(f"{self.level_time.current_time:.2f}") % when != 0:
            return

        number_of_enemies = randrange(amount_from, amount_until + 1) # +1 'cause it's not inclusive
        counter = 0

        aux_x = (WIDTH // 15)
        aux_y = (HEIGHT // 14)
        range_x = lambda : randrange(aux_x, (WIDTH - GUI_SPACE - aux_x), spacing_x)
        range_y = lambda : randrange(-50, 0, spacing_y)

        while counter < number_of_enemies:

            x1 = range_x()
            y1 = range_y()

            new_enemy = choice(enemy_types)(x1=x1,
                                            y1=y1,
                                            x2=x1 + aux_x,
                                            y2=y1 + aux_y,
                                            can_spawn_outside=True)

            if any([new_enemy.x1 == new_enemy.x2,
                    new_enemy.y1 == new_enemy.y2] +
                    [new_enemy.collides_with_box(enemy)
                        for enemy in self.enemies]):
                continue

            self.enemies.append(new_enemy)
            counter += 1


    def generate_enemies(self) -> None:
        """
        Generates specific types on enemies depending on the
        current game level.
        """

        weak_enemies = (EnemyCommonA, EnemyCommonB)

        if self.game_level in range(6): # until level 5

            self.spawn_enemies(when=5,
                               enemy_types=weak_enemies,
                               amount_from=4,
                               amount_until=6,
                               spacing_x=20,
                               spacing_y=5)

        elif self.game_level in range(6, 11): # until level 10
            ...


    def clear_assets(self) -> None:
        """
        Clears all enemies and bullets in their lists once returned to the main menu.
        """

        self.enemies.clear()
        self.player_bullets.clear()
        self.enemies_bullets.clear()


    def advance_game(self, keys_dict: EventsDict) -> None:
        """
        This function is that one of a wrapper, and advances the state of the game.
        It takes a dictionary of the keys pressed to decide if it counts some timers.
        """

        self.refresh_return_timer(keys_dict)

        if self.is_in_game:

            self.generate_enemies()
            self.exec_enem_trajectory()
            self.exec_enem_bul_trajectory()
            self.exec_player_bul_trajectory()

            self.refresh_timers()

        else:

            self.show_debug_info = False
            self.current_scene.press_cooldown.count(1)

        self.current_scene.refresh_hook()


    def refresh_timers(self) -> None:
        """
        Refreshes all the in-game timers of the game, so that it updates theirs values.
        """

        for pl_timer in self.player.get_timers():
            pl_timer.count(1)

        for timer in self.timers.values():
            timer.count(1)

        for chrono in self.chronometers.values():
            chrono.count(0.01)


    def reset_timers(self) -> None:
        """
        Resets all the in-game timers of the game.
        """

        for timer in self.timers.values():
            timer.reset()

        for pl_timer in self.player.get_timers():
            pl_timer.reset()


    def refresh_return_timer(self, keys_dict: EventsDict) -> None:
        """
        Refreshes the return timer.
        """

        exit_correct_keys = list_repeated_keys("EXIT", load_json(KEYS_PATH))

        if any(keys_dict.get(key, False) for key in exit_correct_keys):

            self.exiting = True
            self.exiting_cooldown.deduct(1 if self.is_in_game else 2)

        else:

            self.exiting = False
            self.exiting_cooldown.reset()
