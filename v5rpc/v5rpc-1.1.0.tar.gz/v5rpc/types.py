"""
This is types and helpers for strategies with PyV5Adapter.
"""
from typing import Optional, List
from enum import Enum, unique


@unique
class Team(Enum):
    Self = 0
    Opponent = 1
    Nobody = 2


@unique
class EventType(Enum):
    JudgeResult = 0
    MatchStart = 1
    MatchStop = 2
    FirstHalfStart = 3
    SecondHalfStart = 4
    OvertimeStart = 5
    PenaltyShootoutStart = 6


@unique
class ResultType(Enum):
    PlaceKick = 0
    GoalKick = 1
    PenaltyKick = 2
    FreeKickRightTop = 3
    FreeKickRightBot = 4
    FreeKickLeftTop = 5
    FreeKickLeftBot = 6


class JudgeResultEvent:
    type: ResultType  # ResultType
    offensive_team: int  # Team
    reason: str


class EventArguments:
    judge_result: Optional[JudgeResultEvent]


@unique
class Version(Enum):
    V1_0 = 0
    V1_1 = 1


class Vector2:
    x: float
    y: float


class Wheel:
    left_speed: float
    right_speed: float


class Robot:
    position: Vector2
    rotation: float
    wheel: Wheel


class Ball:
    position: Vector2


class Field:
    self_robots: List[Robot]
    opponent_robots: List[Robot]
    ball: Ball
    tick: int
