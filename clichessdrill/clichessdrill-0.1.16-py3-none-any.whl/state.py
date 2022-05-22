"""

"""
import chess

from clichessdrill.pieces import Pieces


class State:

    def __init__(self):
        self.board = chess.Board()
        self.played_moves = list()

    def show(self, user_pieces: Pieces):

        if user_pieces == Pieces.WHITE:
            print(self.board)

        if user_pieces == Pieces.BLACK:
            reverse_board = chess.Board()
            reverse_board.clear_board()
            reverse_piece_map = dict()
            for _ix, _piece in self.board.piece_map().items():
                reverse_piece_map[63-_ix] = _piece
            reverse_board.set_piece_map(reverse_piece_map)
            print(reverse_board)

    def apply_move(self, move):
        self.played_moves.append(move)
        self.board.push_san(move)

    def history(self):
        for i in range(0, len(self.played_moves), 2):
            m_id = i % 2 + 1
            hm1 = self.played_moves[i]
            hm2 = self.played_moves[i+1] if i + 1 < len(self.played_moves) else '...'
            print(f'{m_id}: {hm1}\t\t{hm2}')
