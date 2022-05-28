# type: ignore
# -*- coding: utf-8 -*-
'''
WindyGridworld class
==============

This class creates a gridworld (board) in which one square is the goal.
The agent starts from a location and should find the fastest route to the goal.
Wind is a fixed amount of padding based on the location of the agent on the
board.


'''


from random import choice

from ..utils import MNKBoard
from ..subjects import Subject
from ..legacy import ValueSet


def main():
    board = WindyGridworld(h_wind=[1, 1, 1, 1, 1], move_pattern='Q')
    _ = board.register('P1')
    for _ in range(10):
        print(board.state)
        my_action = choice(board.possible_actions)
        board.take_effect(my_action, 1)
        print(my_action.value)
        print(f'{board}')


class WindyGridworld(MNKBoard, Subject):
    '''
    Build an m-by-n grid (using mnkboard super class) in which 1 player can
    play. Player wins if it can get to the goal square.

    Attributes
    ----------
    is_terminated: whether the game finished or not.

    possible_actions: a list of possible actions.

    Methods
    -------
    register: register the player and return its ID or return ID of current
        player.

    take_effect: moves the player on the grid.

    reset: clears the grid.
    '''
    def __init__(self, **kwargs):
        '''
        Initialize an instance of windy gridworld.

        Arguments
        ---------
        dim: dimensions of the grid as a tuple. (default=(5, 5))

        start: (row, column) of the starting square. (default=(0, 0))

        goal: (row, column) of the goal square. (default=(4, 4))

        h_wind: a list of size row that determines the strenghs of the wind.
                (default=0)

        v_wind: a list of size column that determines the strenghs of the wind.
                (default=0)

        move_pattern: whether to choose 'R'ook moves or 'Q'ueen moves.
                      (default='R')

        state_type: board (zero one list), tuple ()
        '''
        self._dim, self._start, self._goal = (5, 5), (0, 0), (4, 4)
        self._move_pattern = 'R'
        self._h_wind, self._v_wind = [0]*5, [0]*5
        self.set_params(**kwargs)
        super().__init__(**kwargs)

        if self._move_pattern.upper() == 'Q':
            moves = ['U', 'D', 'R', 'L', 'UR', 'UL', 'DR', 'DL']
        elif self._move_pattern.upper() == 'R':
            moves = ['U', 'D', 'R', 'L']

        self._default_moves = ValueSet(
            moves, binary=lambda x: (moves.index(x), len(moves))
        ).as_valueset_array()

        super().__init__(m=self._dim[0], n=self._dim[1], players=1)
        self.reset()

    @property
    def is_terminated(self):
        '''Return True if the player get to the goal.'''
        return [*self._player_location] == [*self._goal]

    @property
    def state(self):
        '''Return the state of the board as a ValueSet.'''
        return ValueSet(
            self._player_location,
            binary=lambda x: (x[0]*self._dim[1] + x[1], len(self._board)))

    @property
    def possible_actions(self):
        '''Return the set of possible moves.'''
        return self._default_moves

    def register(self, player_name):
        '''
        Register an agent and return its ID.

        If the agent is new, a new ID is generated and the agent_name is added
        to agent_list.
        Arguments
        ---------
        agent_name: the name of the agent to be registered.

        Raises ValueError for an attempt to register more than one agent.
        '''
        if len(self._agent_list) == 0:
            return Subject.register(self, player_name)
        raise ValueError('Windy Gridworld only accepts one player.')

    def _take_effect(self, action, _id=None):
        '''
        Move according to the action.

        Arguments
        ---------
        _id: ID of the player.

        action: the location in which the piece is set. Can be either in index
                format or row column format.
        '''
        row, column = [*self._player_location]
        max_row, max_column = self._dim[0]-1, self._dim[1]-1
        MNKBoard.clear_square(self, row=row, column=column)

        a = str(*action.value)
        if a in ['U', 'UR', 'UL']:
            # min(max(row-1+self._v_wind[column], 0), max_row)
            self._player_location[0] = row - 1
        if a in ['D', 'DR', 'DL']:
            # max(min(row+1+self._v_wind[column], max_row), 0)
            self._player_location[0] = row + 1
        if a in ['L', 'UL', 'DL']:
            # min(max(column-1+self._h_wind[row], 0), max_column)
            self._player_location[1] = column - 1
        if a in ['R', 'UR', 'DR']:
            # max(min(column+1+self._h_wind[row], max_column), 0)
            self._player_location[1] = column + 1

        self._player_location[0] = min(max(
            self._player_location[0]+self._v_wind[column], 0), max_row)
        self._player_location[1] = min(max(
            self._player_location[1]+self._h_wind[row], 0), max_column)

        MNKBoard.set_piece(
            self, player=1,
            row=self._player_location[0], column=self._player_location[1])
        if self.is_terminated:
            return 1
        return -1

    def reset(self):
        '''Clear the board and update board_status.'''
        MNKBoard.reset(self)
        self._player_location = [*self._start]
        MNKBoard.set_piece(
            self, player=1,
            row=self._player_location[0], column=self._player_location[1])

    def __repr__(self):
        return 'WindyGridworld'


if __name__ == '__main__':
    main()
