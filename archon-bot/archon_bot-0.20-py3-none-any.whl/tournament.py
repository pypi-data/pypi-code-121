import collections
import enum
import functools
import itertools
import logging
import math
import os
import random
from typing import Callable, Dict, Generator, List, Optional, Tuple, Union

import aiohttp
import asgiref.sync
import hikari
import krcg.deck
import krcg.seating
import krcg.utils

logger = logging.getLogger()
ITERATIONS = 50000
VEKN_LOGIN = os.getenv("VEKN_LOGIN")
VEKN_PASSWORD = os.getenv("VEKN_PASSWORD")


class CommandFailed(Exception):
    """A "normal" failure: a message explains why the command was not performed"""


class ErrorDecklistRequired(CommandFailed):
    """Specific error for missing decklist, to be able to provide a convenient clue"""


class TournamentFlag(enum.IntFlag):
    VEKN_REQUIRED = enum.auto()  # whether a VEKN ID# is required for this tournament
    DECKLIST_REQUIRED = enum.auto()  # whether a decklist must be submitted
    CHECKIN_EACH_ROUND = enum.auto()  # whether players must check-in at every round
    LEAGUE = enum.auto()  # in a league, players can register between rounds
    STAGGERED = enum.auto()  # whether this is a staggered (6, 7, 11) tournament


class TournamentState(str, enum.Enum):
    REGISTRATION = "REGISTRATION"  # tournament has not begun, registration is open
    CHECKIN = "CHECKIN"  # check-in is open for next round
    PLAYING = "PLAYING"  # round in progress
    WAITING = "WAITING"  # round finished, waiting for next round
    FINISHED = "FINISHED"  # tournament is finished, finals have been played


class DropReason(str, enum.Enum):
    DROP = "DROP"
    DISQUALIFIED = "DISQUALIFIED"


class NoteLevel(str, enum.Enum):
    NOTE = "NOTE"
    OVERRIDE = "OVERRIDE"
    CAUTION = "CAUTION"
    WARNING = "WARNING"


class PlayerStatus(str, enum.Enum):
    CHECKED_IN = "CHECKED_IN"
    CHECKIN_REQUIRED = "CHECKIN_REQUIRED"
    DISQUALIFIED = "DISQUALIFIED"
    PLAYING = "PLAYING"
    MISSING_DECK = "DECK"
    WAITING = "WAITING"
    CHECKED_OUT = "CHECKED_OUT"


class Note:
    def __init__(self, **kwargs):
        self.judge: hikari.Snowflake = hikari.Snowflake(kwargs.get("judge", 0))
        self.level: NoteLevel = NoteLevel(kwargs.get("level", ""))
        self.text: str = kwargs.get("text", "")

    def to_json(self) -> dict:
        return {
            "judge": self.judge,
            "level": self.level,
            "text": self.text,
        }


@functools.total_ordering
class Score:
    def __init__(self, **kwargs):
        self.gw: int = int(kwargs.get("gw", 0))
        self.vp: float = float(kwargs.get("vp", 0))
        self.tp: int = int(kwargs.get("tp", 0))

    def __eq__(self, rhs):
        return (self.gw, self.vp, self.tp) == (rhs.gw, rhs.vp, rhs.tp)

    def __lt__(self, rhs):
        return (self.gw, self.vp, self.tp) < (rhs.gw, rhs.vp, rhs.tp)

    def __str__(self):
        return f"({self.gw}GW{self.vp}, {self.tp}TP)"

    def __add__(self, rhs):
        return self.__class__(
            gw=self.gw + rhs.gw, vp=self.vp + rhs.vp, tp=self.tp + rhs.tp
        )

    def __iadd__(self, rhs):
        self.gw += rhs.gw
        self.vp += rhs.vp
        self.tp += rhs.tp
        return self

    def to_json(self) -> dict:
        return {
            "gw": self.gw,
            "vp": self.vp,
            "tp": self.tp,
        }


class Round:
    def __init__(self, **kwargs):
        self.seating: krcg.seating.Round = krcg.seating.Round(kwargs.get("seating", []))
        self.results: Dict[str, Score] = {
            int(k): Score(**v) for k, v in kwargs.get("results", {}).items()
        }
        self.finals: bool = kwargs.get("finals", False)
        self.overrides: Dict[int, Note] = {
            int(k): Note(**n) for k, n in kwargs.get("overrides", {}).items()
        }
        self.incorrect: List[int] = [int(i) for i in kwargs.get("incorrect", [])]

    def to_json(self) -> dict:
        return {
            "seating": self.seating,
            "results": {k: s.to_json() for k, s in self.results.items()},
            "finals": self.finals,
            "overrides": {k: n.to_json() for k, n in self.overrides.items()},
            "incorrect": self.incorrect,
        }

    def score(self) -> None:
        self.incorrect.clear()
        if not self.seating:
            return
        for i, table in enumerate(self.seating.iter_tables(), 1):
            tps = [12, 24, 36, 48, 60]
            if len(table) == 4:
                tps.pop(2)
            scores = sorted(
                [self.results.get(number, Score()).vp, number] for number in table
            )
            for vp, players in itertools.groupby(scores, lambda a: a[0]):
                players = list(players)
                tp = sum(tps.pop(0) for _ in range(len(players))) // len(players)
                gw = 1 if tp == 60 and vp >= 2 else 0
                for _, number in players:
                    self.results[number] = Score(gw=gw, vp=vp, tp=tp)
            if i not in self.overrides and sum(math.ceil(a[0]) for a in scores) != len(
                table
            ):
                self.incorrect.append(i)
            if not self.finals:
                scores = [self.results.get(number, Score()).vp for number in table]
                for j, score in enumerate(scores):
                    if score % 1 and scores[j - 1] >= 1:
                        self.incorrect.append(i)


class Player:
    def __init__(self, **kwargs):
        self.name: str = kwargs.get("name", "")
        self.vekn: str = kwargs.get("vekn", "")
        self.discord: hikari.Snowflake = hikari.Snowflake(kwargs.get("discord") or 0)
        self.number: int = kwargs.get("number", 0)
        self.deck: dict = kwargs.get("deck", {})
        self.playing: bool = kwargs.get("playing", False)
        self.seed: int = kwargs.get("seed", 0)

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "vekn": self.vekn,
            "discord": self.discord,
            "number": self.number,
            "deck": self.deck,
            "playing": self.playing,
            "seed": self.seed,
        }

    def __hash__(self) -> int:
        return hash(self.vekn)

    def __eq__(self, rhs):
        return self.vekn == rhs.vekn

    def __str__(self):
        s = f"#{self.vekn}"
        if self.name:
            s = f"{self.name} " + s
        if self.discord:
            s += f" <@{self.discord}>"
        return s


PlayerID = Union[str, hikari.Snowflake, int]
Rank = Tuple[int, str, Score]


class PlayerDict(dict):
    """Dictionnary of players.

    TODO: compose instead, serialize next_number to avoid acrobatics (breaking change)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.count = 0
        self.next_number = 1

    def add(self, player: Player):
        if not player.vekn:
            return
        if player.discord:
            self[player.discord] = player
        if player.vekn in self:
            return
        self[player.vekn] = player
        player.number = self.next_number
        self[player.number] = player
        self.count += 1
        self.next_number += 1

    def remove(self, player_id: PlayerID):
        if not player_id:
            return
        number = self[player_id].number
        discord = self[player_id].discord
        vekn = self[player_id].vekn
        del self[vekn]
        del self[number]
        if discord:
            del self[discord]
        self.count -= 1
        # next_number must not be decreased

    def iter_players(self) -> Generator[Player, None, None]:
        for k, v in self.items():
            if isinstance(k, str):
                yield v


class Tournament:
    """Tournament data and base methods"""

    # Keys for roles
    JUDGE = "JUDGE"
    SPECTATOR = "SPECTATOR"
    PLAYER = "PLAYER"

    # Keys for channels
    JUDGE_TEXT = "JUDGES-TEXT"
    JUDGE_VOICE = "JUDGES-VOICE"

    def __init__(self, **kwargs):
        self.name: str = kwargs.get("name", "")
        self.flags: TournamentFlag = TournamentFlag(kwargs.get("flags", 0))
        self.roles: Dict[str, hikari.Snowflake] = kwargs.get("roles", {})
        self.channels: Dict[str, hikari.Snowflake] = kwargs.get("channels", {})
        self.max_rounds: int = kwargs.get("max_rounds", 0)
        self.current_round: int = kwargs.get("current_round", 0)
        # TODO use _state and replace access with a property
        self.state: TournamentState = TournamentState(
            kwargs.get("state", TournamentState.REGISTRATION)
        )
        self.players: PlayerDict = PlayerDict()
        for p in kwargs.get("players", []):
            self.players.add(Player(**p))
        self.players.next_number = (
            max([p.number for p in self.players.iter_players()] + [0]) + 1
        )
        self.dropped: Dict[str, DropReason] = {
            k: DropReason(v) for k, v in kwargs.get("dropped", {}).items()
        }
        self.rounds: List[Round] = [Round(**r) for r in kwargs.get("rounds", [])]
        self.notes: Dict[str, List[Note]] = {
            k: [Note(**x) for x in v] for k, v in kwargs.get("notes", {}).items()
        }
        self.winner: str = kwargs.get("winner", "")

    def __bool__(self):
        return bool(self.name)

    @property
    def prefix(self):
        return "".join([w[0] for w in self.name.split()][:3]) + "-"

    def table_name(self, table_num):
        return f"{self.prefix}Table-{table_num}"

    def to_json(self):
        return {
            "name": self.name,
            "flags": self.flags,
            "roles": self.roles,
            "channels": self.channels,
            "max_rounds": self.max_rounds,
            "current_round": self.current_round,
            "state": self.state,
            "players": [p.to_json() for p in self.players.iter_players()],
            "dropped": self.dropped,
            "rounds": [r.to_json() for r in self.rounds],
            "notes": {k: [n.to_json() for n in v] for k, v in self.notes.items()},
            "winner": self.winner,
        }

    async def add_player(
        self,
        vekn: Optional[str] = None,
        name: Optional[str] = None,
        discord: hikari.Snowflakeish = 0,
        deck: Optional[krcg.deck.Deck] = None,
        judge: bool = False,
    ) -> Player:
        """Used for both check-in and registration.

        It can be called multiple times to fill in the player info piece by piece
        """
        # figure out the VEKN if not provided
        # a temporary ID prefied with "P-" can be assigned if a judge calls the command
        # or if a VEKN is not required for this tournament (ie. unsanctioned)
        temp_vekn = False
        if not vekn:
            if discord and discord in self.players:
                vekn = self.players[discord].vekn
            elif self.flags & TournamentFlag.VEKN_REQUIRED and not judge:
                raise CommandFailed(
                    "Only a judge can register a player without VEKN ID#"
                )
            else:
                vekn = f"P-{self.players.count + 1}"
                temp_vekn = True
        # make sure not to overwrite a previous registration with the same VEKN ID
        # only a judge can override a previous vekn use
        # except if the previous player has dropped
        vekn = str(vekn)  # ensure string so it does not collide with player.number
        if vekn[0] == "#":
            vekn = vekn[1:]
        if vekn in self.players:
            if vekn in self.dropped:
                if not judge and self.dropped[vekn] == DropReason.DISQUALIFIED:
                    raise CommandFailed(
                        "Player was disqualified: only a judge can reinstate them"
                    )
                del self.dropped[vekn]
            if (
                discord
                and self.players[vekn].discord
                and self.players[vekn].discord != discord
            ):
                raise CommandFailed(
                    "Another player has already registered with this ID"
                )
        else:
            if self.flags & TournamentFlag.STAGGERED:
                raise CommandFailed(
                    "Tournament is staggered, no more registration allowed."
                )
        # check deck is tournament legal
        if deck:
            if (
                not judge
                and self.current_round
                and not self.flags & TournamentFlag.LEAGUE
            ):
                raise CommandFailed(
                    "The tournament has started: too late to change deck"
                )
            library_count = deck.cards_count(lambda c: c.library)
            crypt_count = deck.cards_count(lambda c: c.crypt)
            if library_count < 60:
                raise CommandFailed(f"Too few library cards ({library_count} < 60)")
            if library_count > 90:
                raise CommandFailed(f"Too many library cards ({library_count} > 90)")
            if crypt_count < 12:
                raise CommandFailed(f"Too few crypt cards ({crypt_count} < 12)")
            groups = set(c.group for c, _ in deck.cards(lambda c: c.crypt))
            groups.discard("ANY")
            groups = list(groups)
            if len(groups) > 2 or abs(int(groups[0]) - int(groups[-1])) > 1:
                raise CommandFailed("Invalid grouping in crypt")
            banned = [c.name for c, _ in deck.cards(lambda c: c.banned)]
            if any(banned):
                raise CommandFailed(f"Banned cards included: {banned}")
        # upsert the player info
        if not judge and self.current_round and not self.flags & TournamentFlag.LEAGUE:
            if vekn in self.players and deck:
                raise CommandFailed("Tournament in progress: too late to change deck.")
            raise CommandFailed("Tournament in progress: too late to register.")
        if vekn in self.players:
            player = self.players[vekn]
            if name:
                player.name = name
            if discord:
                player.discord = discord
            if deck:
                player.deck = deck.to_json()
            player.playing = self.state == TournamentState.CHECKIN
        else:
            if vekn and not temp_vekn:
                name = await self._check_vekn(vekn)
            if discord in self.players:
                name = name or self.players[discord].name
                deck = deck or self.players[discord].deck
                self.players.remove(discord)
            player = Player(
                vekn=vekn,
                name=name,
                discord=discord,
                deck=deck.to_json() if deck else {},
                playing=self.state == TournamentState.CHECKIN,
            )
            self.players.add(player)
        # decklist requirement on check-in
        if (
            player.playing
            and self.flags & TournamentFlag.DECKLIST_REQUIRED
            and not player.deck
        ):
            raise ErrorDecklistRequired("A decklist is required to participate")
        return player

    async def _check_vekn(self, vekn: str) -> str:
        logger.info("Checking VEKN# %s", vekn)
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://www.vekn.net/api/vekn/login",
                data={"username": VEKN_LOGIN, "password": VEKN_PASSWORD},
            ) as response:
                result = await response.json()
                try:
                    token = result["data"]["auth"]
                except:  # noqa: E722
                    token = None
            if not token:
                raise CommandFailed("Unable to authentify to VEKN")

            async with session.get(
                f"https://www.vekn.net/api/vekn/registry?filter={vekn}",
                headers={"Authorization": f"Bearer {token}"},
            ) as response:
                result = await response.json()
                result = result["data"]
                if isinstance(result, str):
                    raise CommandFailed(f"VEKN returned an error: {result}")
                result = result["players"]
                if len(result) > 1:
                    raise CommandFailed("Incomplete VEKN ID#")
                if len(result) < 1:
                    raise CommandFailed("VEKN ID# not found")
                result = result[0]
                if result["veknid"] != str(vekn):
                    raise CommandFailed("VEKN ID# not found")
                return result["firstname"] + " " + result["lastname"]

    def _check_player_id(self, player_id: PlayerID) -> str:
        if player_id not in self.players:
            raise CommandFailed("Player is not registered")
        return self.players[player_id].vekn

    def drop(
        self,
        player_id: PlayerID,
        reason: DropReason = DropReason.DROP,
    ) -> None:
        """Remove a player from the tournament.

        It's either recorded as DropReason.DROP or DropReason.DISQUALIFIED.
        Voluntary drops can always come back in a later round.
        Disqualified players cannot only be reinstated by a judge.
        """
        vekn = self._check_player_id(player_id)
        if self.dropped.get(vekn, None) == DropReason.DISQUALIFIED:
            raise CommandFailed("Player is already disqualified")
        elif not self.rounds:
            self.players.remove(vekn)
            self.dropped.pop(vekn, None)
        else:
            self.dropped[vekn] = reason
            self.players[vekn].playing = False

    def _reset_checkin(self) -> None:
        for player in self.players.iter_players():
            player.playing = False

    def open_registrations(self) -> None:
        if self.state == TournamentState.PLAYING:
            raise CommandFailed("Round in progress: registrations cannot be open")
        if self.state == TournamentState.CHECKIN:
            raise CommandFailed("Check-in in progress: registrations are open")
        # REGISTRATION, WAITING
        if self.flags & TournamentFlag.STAGGERED:
            raise CommandFailed("Tournament is staggered: cannot open registrations")
        self._reset_checkin()
        self.state = TournamentState.REGISTRATION

    def open_checkin(self) -> None:
        if self.flags & TournamentFlag.STAGGERED:
            raise CommandFailed("No check-in for staggered tournaments")
        if self.state == TournamentState.PLAYING:
            raise CommandFailed("The current round must be finished first")
        if self.state != TournamentState.CHECKIN:
            self._reset_checkin()
        # REGISTRATION, WAITING and CHECKIN
        self.state = TournamentState.CHECKIN

    def close_checkin(self) -> None:
        if self.state == TournamentState.CHECKIN:
            self.state = TournamentState.WAITING
        # REGISTRATION, WAITING and PLAYING stay as is

    async def start_round(self, progression_callback: Callable) -> Round:
        if self.state == TournamentState.REGISTRATION:
            raise CommandFailed("Check players in before starting the round")
        if self.state == TournamentState.PLAYING:
            raise CommandFailed("Finish the previous round before starting a new one")
        if self.state == TournamentState.FINISHED:
            raise CommandFailed("Tournament is finished")
        self.current_round += 1
        self.state = TournamentState.PLAYING
        if self.flags & TournamentFlag.STAGGERED:
            round = self.rounds[self.current_round - 1].seating
            playing = set(round.iter_players())
            for player in self.players.iter_players():
                player.playing = player.number in playing
            return self.rounds[self.current_round - 1]
        # non-staggered
        players = [p.number for p in self.players.iter_players() if p.playing]
        if len(players) < 4:
            raise CommandFailed("More players are required")
        if len(players) in [6, 7, 11] and not (self.flags & TournamentFlag.STAGGERED):
            raise CommandFailed(
                "A staggered tournament structure is required for 6, 7 or 11 players"
            )
        round = krcg.seating.Round.from_players(players)
        round.shuffle()
        self.rounds.append(Round(seating=round))
        if self.current_round > 1:
            optimised_rounds, score = await asgiref.sync.sync_to_async(
                krcg.seating.optimise
            )(
                rounds=[r.seating for r in self.rounds],
                iterations=ITERATIONS,
                fixed=self.current_round - 1,
                callback=asgiref.sync.async_to_sync(progression_callback),
            )
            logger.info(
                "{self.name}: optimised seating for round %s with score %s",
                self.current_round,
                score,
            )
            self.rounds[-1].seating = optimised_rounds[-1]
        return self.rounds[-1]

    async def make_staggered(
        self, rounds_count: int, progression_callback: Callable
    ) -> None:
        """Make a tournament "staggered"

        For 6, 7 or 11 players only, use more rounds with players seating out some of
        them so that in the end everyone has played the same number of rounds.

        - rounds_count: number of rounds each player gets to play
        - callback is called every 100th of the way with arguments:
            * step
            * temperature
            * score
            * trials (since last callback call)
            * accepts (since last callback call)
            * improves (since last callback call)
        """
        if self.flags & TournamentFlag.STAGGERED:
            return
        if self.rounds:
            raise CommandFailed(
                "The tournament has already started: staggering is not possible anymore"
            )
        players = [p.number for p in self.players.iter_players() if p.playing]
        if len(players) not in [6, 7, 11]:
            raise CommandFailed(
                "A staggered tournament requires exactly 6, 7 or 11 players"
            )
        rounds = krcg.seating.get_rounds(len(players), rounds_count)
        rounds, score = await asgiref.sync.sync_to_async(krcg.seating.optimise)(
            rounds=self.rounds,
            iterations=ITERATIONS,
            fixed=0,
            callback=asgiref.sync.async_to_sync(progression_callback),
        )
        self.rounds = [Round(seating=r) for r in rounds]
        logger.info(
            "{self.name}: optimised seating for %s rounds with score %s",
            rounds_count,
            score,
        )
        self.flags |= TournamentFlag.STAGGERED
        self.state = TournamentState.WAITING

    def unmake_staggered(self) -> None:
        if not (self.flags & TournamentFlag.STAGGERED):
            return
        if self.current_round:
            raise CommandFailed(
                "The tournament has started: unable to modify its structure"
            )
        self.rounds = []
        self.flags ^= TournamentFlag.STAGGERED

    def round_add(self, player_id: PlayerID, table_num: int) -> None:
        """Add a player to the given table in current round.

        A convenience feature to add a late incoming player to a tournament,
        if by chance there is a 4 players table that hasn't started playing yet.
        """
        if self.flags & TournamentFlag.STAGGERED:
            raise CommandFailed("Cannot add a player in a staggered tournament")
        if player_id not in self.players:
            raise CommandFailed("User is not registered")
        player = self.players[player_id]
        # if not player.playing:
        #     raise CommandFailed("User is not playing this round")
        if not self.rounds:
            raise CommandFailed("No round in progress")
        if table_num > len(self.rounds[-1].seating) or table_num < 1:
            raise CommandFailed("Invalid table number")
        table = self.rounds[-1].seating[table_num - 1]
        if len(table) > 4:
            raise CommandFailed("Table has 5 players already")
        table.append(player.number)
        player.playing = True
        # if this is not first round, optimise the score
        # and make sure we don't repeat a predator-prey relation
        if len(self.rounds) > 1:
            self._optimise_table(table_num)

    def round_remove(self, player_id: PlayerID) -> int:
        """Remove a player from current round, returns the table number.

        A convenience feature to remove a late player from a round before starting,
        if by chance they were seated on a 5 players table.
        It is especially useful for handling unexpected drops during a tournament:
        if the player simply walks away between rounds and does not present himself
        on the table, you want to reorganise the seating if possible, to avoid
        repeating predator-prey relationships.
        """
        if self.flags & TournamentFlag.STAGGERED:
            raise CommandFailed("Cannot remove a player from a staggered tournament")
        if player_id not in self.players:
            raise CommandFailed("User is not registered")
        player = self.players[player_id]
        if not self.rounds:
            raise CommandFailed("No round in progress")
        for table_num, _, _, p in self.rounds[-1].seating.iter_table_players():
            if player.number == p:
                break
        else:
            raise CommandFailed("User is not playing this round")
        table = self.rounds[-1].seating[table_num - 1]
        if len(table) < 5:
            raise CommandFailed("Table has only 4 players, unable to remove one.")
        table.remove(player.number)
        player.playing = False
        # if this is not first round, optimise the score
        # and make sure we don't repeat a predator-prey relation
        if len(self.rounds) > 1:
            self._optimise_table(table_num)
        return table_num

    def _optimise_table(self, table_num: int):
        """For round add/remove: optimise the modified table seating score."""
        max_number = max(
            p.number
            for p in itertools.chain.from_iterable(
                r.seating.iter_players() for r in self.rounds
            )
        )
        base = sum(
            krcg.seating.measure(max_number, r.seating) for r in self.rounds[:-1]
        )
        table = self.rounds[-1].seating[table_num - 1]
        best_table = table
        best_score = math.inf
        # max 120 possibilities, we check them all for the best score
        for new_table in itertools.permutations(table):
            self.rounds[-1].seating[table_num - 1] = new_table
            measure = krcg.seating.measure(max_number, self.rounds[-1].seating)
            new_score = krcg.seating.Score.fast_total(base + measure)
            if new_score < best_score:
                best_score = new_score
                best_table = new_table
        self.rounds[-1].seating[table_num - 1] = best_table

    def finish_round(self, keep_checkin=False) -> Round:
        """Mark the round as finished. Score gets frozen."""
        if not self.rounds or self.state != TournamentState.PLAYING:
            raise CommandFailed("No round in progress")
        self.rounds[-1].score()
        incorrect = self.rounds[-1].incorrect
        if len(incorrect) > 1:
            raise CommandFailed(f"Incorrect score for tables {incorrect}")
        if len(incorrect) > 0:
            raise CommandFailed(f"Incorrect score for table {incorrect[0]}")
        if self.rounds[-1].finals:
            self.state = TournamentState.FINISHED
            self._reset_checkin()
            self.standings()  # compute the winner
        else:
            self.state = TournamentState.WAITING
            if self.flags & TournamentFlag.CHECKIN_EACH_ROUND and not keep_checkin:
                self._reset_checkin()
        return self.rounds[-1]

    def reset_round(self) -> Round:
        """Reset the current round. You can then start it anew using `start_round`."""
        if not self.rounds:
            raise CommandFailed("No round in progress")
        if self.rounds[-1].results:
            raise CommandFailed(
                "Some rounds results have been entered, the round cannot be reset."
            )
        round = self.rounds.pop(-1)
        self.current_round -= 1
        if round.finals:
            self.state = TournamentState.WAITING
        else:
            self.state = TournamentState.CHECKIN
        return round

    def _check_round_number(self, round_number: Optional[int] = None) -> int:
        """Return the actual round_number.

        None defaults to last round.
        """
        if round_number is None:
            return len(self.rounds)
        if round_number < 1:
            raise CommandFailed(f"Invalid round number {round_number}")
        if round_number >= len(self.rounds):
            raise CommandFailed(f"Round {round_number} has yet to be played")
        return round_number

    def report(
        self,
        player_id: PlayerID,
        vps: float = 0,
        round_number: Optional[int] = None,
    ) -> None:
        """Report the number of VPs scored.

        round_number defaults to the current round.
        """
        if self.state != TournamentState.PLAYING:
            raise CommandFailed("Scores can only be reported when a round is ongoing")
        round_number = self._check_round_number(round_number)
        try:
            player = self.players[player_id]
        except KeyError:
            raise CommandFailed("Player is not registers")
        round = self.rounds[round_number - 1]
        if player.number not in set(round.seating.iter_players()):
            raise CommandFailed("Player was not playing in that round")
        # do not let disqualified players enter VPs even if they were playing the round
        if self.dropped.get(player.vekn, None) == DropReason.DISQUALIFIED:
            raise CommandFailed("Player has been disqualified")
        if vps not in {0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5}:
            raise CommandFailed("VPs must be between 0 and 5")
        round.results[player.number] = Score(vp=vps)

    def standings(self, toss=False) -> Tuple[Optional[str], List[Rank]]:
        """Return the winner (if any) and a full ranking [(rank, vekn, score)]

        If checking standings for finals list, toss should be True so that equal ranks
        get order randomly. In that case, record the seed order in Player.seed so that
        anyone winning a toss keeps their rank on subsequent calls, typically
        if the finals seating gets rollbacked because a finalist is missing.
        """
        winner = None
        for i, round in enumerate(
            self.rounds[: -1 if self.state == TournamentState.PLAYING else None], 1
        ):
            # check scores again, some VPs fixes might have happened
            round.score()
            if round.incorrect:
                if len(round.incorrect) > 1:
                    raise CommandFailed(
                        f"Incorrect score for tables {round.incorrect} in round {i}"
                    )
                if len(round.incorrect) > 0:
                    raise CommandFailed(
                        f"Incorrect score for table {round.incorrect[0]} in round {i}"
                    )
            if round.finals and round.results:
                winner = max(
                    round.results.items(),
                    key=lambda a: (a[1], -self.players[a[0]].seed),
                )[0]
                # winning the finals counts as a GW even with less than 2 VPs
                # cf. VEKN Ratings system
                round.results[winner].gw = 1
        totals = collections.defaultdict(Score)
        for round in self.rounds:
            for number, score in round.results.items():
                totals[number] += score
        ranking = []
        last = Score()
        rank = 1
        for j, (number, score) in enumerate(
            sorted(
                totals.items(),
                key=lambda a: (
                    self.players[a[0]].vekn not in self.dropped,
                    winner == a[0],
                    a[1],
                    # put the seed here, so if you win the toss once, you keep your win
                    # 0 would go before negative seed numbers, math.nan always goes last
                    # BUG: this does not seem to work, check it
                    -self.players[a[0]].seed or math.nan,
                    # toss
                    random.random() if toss else a[0],
                ),
                reverse=True,
            ),
            1,
        ):
            vekn = self.players[number].vekn
            if vekn not in self.dropped:
                if winner and 1 < j < 6:
                    rank = 2
                elif last != score:
                    rank = j
                last = score
            if vekn in self.dropped and last is not None:
                last = None
                rank = j
            ranking.append((rank, vekn, score))
        self.winner = self.players[winner].vekn if winner else ""
        return winner, ranking

    def start_finals(self) -> Round:
        _, ranking = self.standings(toss=True)  # toss for finals seats if necessary
        top_5 = [self.players[vekn].number for (_rank, vekn, _score) in ranking[:5]]
        for p in self.players.iter_players():
            p.seed = 0
            p.playing = False
        for i, number in enumerate(top_5, 1):
            self.players[number].seed = i
            self.players[number].playing = True
        # note register "seating" for finals is in fact seeding order
        # actual seating is not (yet) recorded
        self.current_round += 1
        self.rounds.append(
            Round(finals=True, seating=krcg.seating.Round.from_players(top_5))
        )
        self.state = TournamentState.PLAYING
        return self.rounds[-1]

    def rollback_round(self) -> None:
        if not self.rounds:
            raise CommandFailed("No round")
        if self.rounds[-1].results:
            raise CommandFailed("Round has been played")
        self.rounds.pop(-1)
        self.current_round -= 1
        self.state = TournamentState.WAITING

    def note(
        self,
        player_id: PlayerID,
        judge: hikari.Snowflake,
        level: NoteLevel,
        comment: str,
    ) -> None:
        """Take a note concerning a given player (judge command).

        Repeated NoteLevel.CAUTION should lead to a WARNING,
        Repeated NoteLevel.WARNING should lead to a disqualification (cf. drop())
        """
        vekn = self._check_player_id(player_id)
        self.notes.setdefault(vekn, [])
        self.notes[vekn].append(
            Note(
                judge=judge,
                level=level,
                text=comment,
            )
        )

    def validate_score(
        self,
        table_number: int,
        judge: hikari.Snowflake,
        comment: str,
        round_number: Optional[int] = None,
    ) -> None:
        """Validate an odd score situation on a given table.

        This typically happens when a player drops or is disqualified and the expected
        VP is not or only partially attributed by the judge.
        """
        round_number = self._check_round_number(round_number)
        round = self.rounds[round_number - 1]
        if table_number < 1 or table_number > len(round.seating):
            raise CommandFailed("Invalid table number")
        round.overrides[table_number] = Note(
            level=NoteLevel.OVERRIDE, judge=judge, text=comment
        )

    def player_info(self, vekn_or_discord: PlayerID):
        """Returns a player information (PlayerInfo instance)"""
        vekn = self._check_player_id(vekn_or_discord)
        return PlayerInfo(vekn, self)


class PlayerInfo:
    player = None
    table = None
    position = None
    rounds = None
    score = None
    status = None
    drop = None
    notes = None

    def __init__(self, vekn: str, tournament: Tournament):
        self.player = tournament.players[vekn]
        self.drop = tournament.dropped.get(vekn, None)
        self.notes = tournament.notes.get(vekn, [])
        if self.drop and self.drop == DropReason.DISQUALIFIED:
            self.status = PlayerStatus.DISQUALIFIED
        else:
            if (
                not self.player.deck
                and tournament.flags & TournamentFlag.DECKLIST_REQUIRED
            ):
                self.status = PlayerStatus.MISSING_DECK
            elif tournament.state == TournamentState.REGISTRATION:
                self.status = PlayerStatus.WAITING
            elif tournament.state == TournamentState.WAITING:
                if (
                    tournament.current_round == 0
                    or self.player.playing
                    or tournament.flags & TournamentFlag.CHECKIN_EACH_ROUND
                ):
                    self.status = PlayerStatus.WAITING
                else:
                    self.status = PlayerStatus.CHECKED_OUT
            elif tournament.state == TournamentState.CHECKIN:
                if self.player.playing:
                    self.status = PlayerStatus.CHECKED_IN
                else:
                    self.status = PlayerStatus.CHECKIN_REQUIRED
            elif tournament.state == TournamentState.FINISHED:
                self.status = PlayerStatus.WAITING
            # round in progress
            else:
                if self.player.playing:
                    self.status = PlayerStatus.PLAYING
                else:  # player has a deck but is not playing
                    self.status = PlayerStatus.CHECKED_OUT
        self.score = Score()
        self.rounds = 0
        for i, round in enumerate(tournament.rounds, 1):
            if self.player.number in round.seating.iter_players():
                self.rounds += 1
                if i == tournament.current_round:
                    for (
                        table,
                        position,
                        _size,
                        player,
                    ) in round.seating.iter_table_players():
                        if player == self.player.number:
                            self.table = table
                            self.position = position
                            break
            self.score += round.results.get(self.player.number, Score())

    def __str__(self):
        return (
            f"player: {self.player}, table: {self.table}, position: {self.position}, "
            f"rounds: {self.rounds}, score: {self.score}, status: {self.status}, "
            f"drop: {self.drop}, notes: {self.notes}"
        )
