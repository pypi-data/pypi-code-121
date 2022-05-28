from typing import Optional
from pydantic import BaseModel


class TeamResult(BaseModel):
    key: str
    name: str


class FrequentSkill(BaseModel):
    id: str
    name: str
    image: str


class GearBrand(BaseModel):
    id: str
    name: str
    frequent_skill: Optional[FrequentSkill]
    image: str


class Gear(BaseModel):
    id: str
    kind: str
    name: str
    rarity: int
    thumbnail: str
    image: str
    brand: GearBrand


class SubWeapon(BaseModel):
    id: str
    name: str
    image_a: str
    image_b: str


class SpecialWeapon(BaseModel):
    id: str
    name: str
    image_a: str
    image_b: str


class Weapon(BaseModel):
    id: str
    name: str
    image: str
    thumbnail: str
    sub: SubWeapon
    special: SpecialWeapon


class Udemae(BaseModel):
    is_number_reached: Optional[bool]
    is_x: bool
    name: str
    number: Optional[int]
    s_plus_number: Optional[int]


class GearSkill(BaseModel):
    id: str
    name: str
    image: str


class GearSkills(BaseModel):
    main: GearSkill
    subs: list[Optional[GearSkill]]


class PlayerType(BaseModel):
    style: str
    species: str


class Player(BaseModel):
    clothes: Gear
    clothes_skills: GearSkills
    head: Gear
    head_skills: GearSkills
    nickname: str
    player_type: PlayerType
    player_rank: int
    principal_id: str
    shoes: Gear
    shoes_skills: GearSkills
    star_rank: int
    udemae: Optional[Udemae]
    weapon: Weapon


class PlayerResult(BaseModel):
    assist_count: int
    death_count: int
    game_paint_point: int
    kill_count: int
    player: Player
    sort_score: int
    special_count: int


class GameMode(BaseModel):
    name: str
    key: str


class Rule(BaseModel):
    key: str
    name: str
    multiline_name: str


class Stage(BaseModel):
    name: str
    image: str
    id: str


class CrownPlayer(BaseModel):
    pass


class Result(BaseModel):
    battle_number: str
    crown_players: Optional[list[CrownPlayer]]
    elapsed_time: Optional[int]
    estimate_gachi_power: Optional[int]
    estimate_x_power: Optional[int]
    game_mode: GameMode
    my_team_count: Optional[int]
    my_team_members: Optional[list[PlayerResult]]
    my_team_percentage: Optional[float]
    my_team_result: TeamResult
    other_team_count: Optional[int]
    other_team_members: Optional[list[PlayerResult]]
    other_team_percentage: Optional[float]
    other_team_result: TeamResult
    player_result: PlayerResult
    player_rank: int
    rank: Optional[int]
    rule: Rule
    stage: Stage
    star_rank: int
    start_time: int
    type: str
    udemae: Optional[Udemae]
    weapon_paint_point: int
    x_power: Optional[float]


class ResultsSummary(BaseModel):
    count: int
    victory_rate: float
    special_count_average: float
    victory_count: int
    defeat_count: int
    kill_count_average: float
    assist_count_average: float
    death_count_average: float


class Results(BaseModel):
    results: list[Result]
    unique_id: str
    summary: ResultsSummary
