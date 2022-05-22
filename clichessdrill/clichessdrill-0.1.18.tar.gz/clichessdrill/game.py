"""
Drill execution
"""
import os
import random
import time
from typing import Dict

from clichessdrill.pieces import Pieces
from clichessdrill.state import State


class Game:

    allowed_attempts = 3

    def __init__(self, plan: Dict, user_pieces: Pieces = Pieces.WHITE):
        random.seed(int(time.time()))
        self.plan = plan
        self.user_pieces = user_pieces
        self.turn = Pieces(0)
        self.subtree = plan['play'][self.user_pieces.name.lower()]
        self.end_reached = False
        self.state = State()

    def execute_move(self):

        if self.turn == self.user_pieces:
            success, move = self.user_move()
            if not success:
                self.end_reached = True
                return False
        else:
            move = self.bot_move()

        self.state.apply_move(move)
        self.turn = Pieces((self.turn.value + 1) % 2)
        self.subtree = self.subtree[move]
        if len(self.subtree.keys()) == 0:
            self.end_reached = True

        return True

    def user_move(self):

        os.system('clear')
        self.state.show(self.user_pieces)
        print(15*'-')
        self.state.history()

        for i in range(self.allowed_attempts):
            move = input(f'your move ({self.turn.name.lower()}): ')

            if move in self.subtree.keys():
                success = True
                return success, move

            print(f'Incorrect move. {self.allowed_attempts - i - 1} attempts left.')

        correct_move = list(self.subtree.keys())[0]
        print(f'You are out of attempts. Correct move: {correct_move}')
        success = False
        move = None
        return success, move

    def bot_move(self):

        possible_moves = list(self.subtree.keys())
        move = random.choice(possible_moves)

        return move

    def run(self):

        while not self.end_reached:
            success = self.execute_move()

        if success:
            os.system('clear')
            self.state.show(self.user_pieces)
            print(15*'-')
            self.state.history()
            print('Good job. You found all correct moves.')
        else:
            print('Keep practicing. You will get there.')
