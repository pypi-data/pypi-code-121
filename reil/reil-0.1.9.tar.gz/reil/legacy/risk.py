# -*- coding: utf-8 -*-
# type: ignore
'''
Risk class
==========

This `subject` class emulates dice throwing in Risk board game. 


'''

from random import randrange

from reil.valueset import ValueSet
from reil.subjects.subject import Subject


def main():
    board = Risk(pieces=[5, 5])
    player = {}
    player['P1'] = board.register('P1')
    player['P2'] = board.register('P2')
    while not board.is_terminated:
        board.take_effect(player['P1'], ValueSet(2))
        board.take_effect(player['P2'], ValueSet(1))
        print(board._pieces)


class Risk(Subject):
    '''

    Attributes
    ----------
        is_terminated: whether the game finished or not.
        possible_actions: a list of possible actions (how many pieces to play).

    Methods
    -------
        register: register a new player and return its ID or return ID of an existing player.
        take_effect: roll the dice and return the result.
        ??? set_piece: set a piece of the specified player on the specified square of the board.
        reset: clear the conditions.
    '''
    # _board is a row vector. (row, column) and index start from 0
    # _board_status: None: no winner yet,
    #                1..players: winner,
    #                0: stall,
    #               -1: illegal board
    def __init__(self, **kwargs):
        '''
        Initialize an instance of risk.

        Arguments
        ---------
            pieces: an array containing the number of peices for players 1 and 2 (default=[3, 2])
        '''
        self._pieces = [3, 2]
        self._turn = 0
        self.set_params(**kwargs)
        super().__init__(**kwargs)

        self._temp = 0

        self._initial_pieces = list(self._pieces)

    @property
    def is_terminated(self):
        '''Return True if no moves is left.'''
        return (self._pieces[0] <= 1) | (self._pieces[1] <= 0)

    @property
    def possible_actions(self):
        '''Return a list of indexes of empty squares.'''
        max_move = min(self._pieces[self._turn], [3, 2][self._turn])
        if self._turn == 1:
            max_move = min(self._temp, max_move)
        try:
            return ValueSet(list(range(1, max_move + 1)), min=1, max=[3, 2][self._turn]).as_valueset_array()
        except TypeError:
            return ValueSet(0, min=0, max=[3, 2][self._turn]).as_valueset_array()

    @property
    def state(self):
        return ValueSet(self._pieces, min=[0, 0], max=self._initial_pieces)

    def register(self, player_name):
        '''
        Register an agent and return its ID.
        
        If the agent is new, a new ID is generated and the agent_name is added to agent_list.
        Arguments
        ---------
            agent_name: the name of the agent to be registered.
        '''
        if len(self._agent_list)<2:
            return Subject.register(self, player_name)

    def take_effect(self, action, _id=None):
        '''
        Set a piece for the given player on the board.

        Arguments
        ---------
            _id: ID of the player who sets the piece.
            action: the location in which the piece is set. Can be either in index format or row column format.
        '''
        if self._turn == 0:
            self._temp = action.value[0]
            self._turn = 1
            return 0
        else:
            # reward = 0
            p1 = list(randrange(6) for _ in range(self._temp))
            p2 = list(randrange(6) for _ in range(action.value[0]))
            for _ in range(min(self._temp, action.value[0])):
                if max(p1)<=max(p2):
                    self._pieces[0] -= 1
                    # reward += 1
                else:
                    self._pieces[1] -= 1
                    # reward -= 1
                p1.remove(max(p1))
                p2.remove(max(p2))

            self._turn = 0
            # return reward
            if self._pieces[0] <= 0:  # player 1 wins, so player 2 loses
                return 1
            elif self._pieces[1] <= 0:
                return -1
            else:
                return 0

    def reset(self):
        '''Clear the board and update board_status.'''
        self._pieces = list(self._initial_pieces)
        self._turn = 0
        self._temp = 0

    def __repr__(self):
        return 'Risk'

if __name__ == '__main__':
    main()
