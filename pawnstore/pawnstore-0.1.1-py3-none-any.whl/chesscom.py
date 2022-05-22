import io

import chess.pgn
import requests
import datetime as dt

from pawnstore.services import ChessPlatform, parse_game, insert_game

ARCHIVES_URL = "https://api.chess.com/pub/player/{}/games/archives"


def opposite(color):
    return "Black" if color.title() == "White" else "White"


class ChesscomError(Exception):
    pass


class Chesscom(ChessPlatform):
    name = "chess.com"
    convert = {"TimeControl": {"300+5": "5+5", "600": "10+0", "900+10": "15+10"}}

    def export_by_player(self, username, num=None, desc=True):
        """Yield num last games of username as json blobs"""

        idx = 0
        try:
            res = requests.get(ARCHIVES_URL.format(username)).json()
        except requests.exceptions.ConnectionError as e:
            print("Connection error: skipping {} import".format(self.name))
            return
        if res.get("code") == 0:
            raise ChesscomError(res["message"])

        archives = res["archives"]
        order = -1 if desc else 1
        for monthly_url in archives[::order]:
            res = requests.get(monthly_url).json()
            games = res["games"][::-1]

            for game in games:
                yield game
                idx += 1
                if idx == num:
                    return

    def _user_result(self, json, color):
        """Return result of the game for side with given color."""
        if json["white"]["result"] == "win":
            termination = json["black"]["result"]
            return ("W" if color == "white" else "L", termination)
        elif json["black"]["result"] == "win":
            termination = json["white"]["result"]
            return ("W" if color == "black" else "L", termination)
        else:  # draw

            return ("D", json[color]["result"])

    def _user_accuracy(self, json, color):
        accuracies = json.get("accuracies")
        if accuracies:
            return accuracies[color]

    def _opening_name(self, url):
        words = url.split("/")[-1].replace("-", " ").split()
        res = []
        for item in words:

            if item[0].isdigit():
                break
            res.append(item)
        return " ".join(res)

    def user_centric(self, json, user):
        """Return game as a dict with fields adopting a user POV."""

        res = {
            "slug": json.get("url", None),
            "pgn": json.get("pgn", None),
            "website": self.name,
            "speed": "bullet",  # TODO
        }

        hdr, moves = parse_game(chess.pgn.read_game(io.StringIO(json["pgn"])))
        color = "white" if (hdr["White"].lower() == user.lower()) else "black"
        res["white"] = color == "white"
        res["eco"] = hdr["ECO"]
        res["eco_name"] = self._opening_name(hdr["ECOUrl"])
        res["elo"] = hdr[color.title() + "Elo"]

        res["opp_name"] = hdr[opposite(color)]

        res["opp_elo"] = hdr[opposite(color) + "Elo"]
        res["time_control"] = self.convert["TimeControl"].get(
            hdr["TimeControl"], hdr["TimeControl"]
        )
        res["user"] = user
        res["accuracy"] = self._user_accuracy(json, color)
        res["moves"] = " ".join(moves)

        res["timestamp"] = dt.datetime.fromtimestamp(json["end_time"])
        res["result"], res["termination"] = self._user_result(json, color.lower())
        return res


CHESSCOM = Chesscom()
