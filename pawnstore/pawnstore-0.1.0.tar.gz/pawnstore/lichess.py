import io
import os

import chess.pgn
import requests
import berserk

import datetime as dt

from pawnstore.services import ChessPlatform, parse_game

LICHESS_API = berserk.Client(berserk.TokenSession(os.environ.get("LICHESS_API_TOKEN")))


class LichessError(Exception):
    pass


class Lichess(ChessPlatform):
    name = "lichess.org"
    convert = {
        "Termination": {
            "mate": "checkmated",
            "resign": "resigned",
            "draw": "",
            "outoftime": "timeout",
        }
    }

    def export_by_player(self, username, max=None):
        return LICHESS_API.games.export_by_player(
            username, as_pgn=False, moves=True, evals=True, opening=True, max=max
        )

    def _user_result(self, json, color):
        """Return result of the game for side with given color."""
        res = "L"
        if json["status"] in ("draw", "stalemate"):
            res = "D"
        elif json["winner"] == color:
            res = "W"
        return res

    def user_centric(self, json, user):
        """Return game as a dict with fields adopting a user POV."""
        game = json
        if "opening" not in json:
            return
        res = {}
        mapping = {
            "createdAt": "timestamp",
            "winner": "result",
        }
        for key in (
            "variant",
            "speed",
            "createdAt",
            "winner",
            "moves",
            "analysis",
            "pgn",
        ):
            res[mapping.get(key, key)] = json.get(key, None)

        res["slug"] = f"https://lichess.org/{json['id']}"
        res["eco"] = json["opening"]["eco"]
        res["eco_name"] = json["opening"]["name"]

        try:
            if json["players"]["white"]["user"]["id"] == user.lower():
                color, opp_color = "white", "black"
            else:
                color, opp_color = "black", "white"
        except KeyError:  # game against AI
            return

        res["white"] = color == "white"
        res["elo"] = json["players"][color]["rating"]
        res["opp_name"] = json["players"][opp_color]["user"]["id"]
        res["opp_elo"] = json["players"][opp_color]["rating"]
        res["website"] = self.name
        res["user"] = user
        res["result"] = self._user_result(json, color)
        res["termination"] = self.convert["Termination"].get(json["status"])
        res["time_control"] = "{total}+{incr}".format(
            total=int(json["clock"]["initial"] / 60), incr=json["clock"]["increment"]
        )

        return res


LICHESS = Lichess()
