import io
import chess.pgn

from peewee import IntegrityError

from .models import Game


def parse_game(game):
    hdr = {**game.headers._tag_roster, **game.headers._others}
    board = chess.Board()
    moves = []
    for x in game.mainline_moves():
        moves.append(board.san(x))
        board.push(x)
    return hdr, moves


def insert_game(game_dict):
    """Insert game in database"""
    if not game_dict or not game_dict.get("slug"):  # ??
        return False
    game = Game.create(**game_dict)
    return True


class ChessPlatform:
    def export_by_player(self, username, num=None):
        """Yield num last games of username as json blobs"""
        raise NotImplementedError

    def user_centric(self, json, user):
        """ """
        raise NotImplementedError

    def sync(self, user, full):
        inserts = 0

        for game in self.export_by_player(user, 100):
            game_dict = self.user_centric(game, user)
            if game_dict:
                try:
                    inserts += insert_game(game_dict)
                except IntegrityError as e:
                    if not full:
                        break  # reached last insert game
        if inserts:
            print(f"{inserts} {self.name} games inserted")
