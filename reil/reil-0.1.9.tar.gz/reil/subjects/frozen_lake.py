# -*- coding: utf-8 -*-
# TODO: Components (state, possible actions, etc.) should be updated
# according to the new implementation of `Subject`.

'''
FrozenLake class
=================

This class creates a frozen lake (board) in which one square is the goal.
The `agent` starts from a location and should find the fastest route to
the goal. Some locations are holes.
'''

from random import choice
from typing import Any, List, Optional, Tuple

from reil.datatypes.feature import (Feature, FeatureGenerator,
                                    FeatureGeneratorSet, FeatureGeneratorType,
                                    FeatureSet)
from reil.subjects.subject import Subject
from reil.utils.mnkboard import MNKBoard


class FrozenLake(MNKBoard, Subject):
    '''
    Build an m-by-n grid (using mnkboard super class) in which 1 player can
    play. Player wins if it can get to the goal square. Each element in the
    graph can be:
        S: starting point, safe
        F: frozen surface, safe
        H: hole (end with reward -1)
        G: goal (end with reward 1)

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
    def __init__(
            self, _map: Optional[List[List[str]]] = None,
            terminate_on_hole: bool = False, **kwargs: Any):
        '''
        Arguments
        ---------
        map:
            the map to be used
        '''
        default_map = [
            ['S', 'F', 'F', 'F'],
            ['F', 'H', 'F', 'H'],
            ['F', 'F', 'F', 'H'],
            ['H', 'F', 'F', 'G']]
        moves = ('U', 'D', 'R', 'L')

        temp_map = _map or default_map
        self._dim = (len(temp_map), len(temp_map[0]))
        self._start = self._locate(temp_map, 'S')
        self._goal = self._locate(temp_map, 'G')
        self._terminate_on_hole = terminate_on_hole

        Subject.__init__(self, max_entity_count=1, **kwargs)
        MNKBoard.__init__(
            self, m=self._dim[0], n=self._dim[1],
            player_names={1: 'P'},
            init_board=[c for r in temp_map for c in r],
            **kwargs)

        self._board_gen = FeatureGenerator.categorical(
            name='board', categories=('S', 'G', 'F', 'H', 'P'))
        self._board_gen.__dict__['normalizer'] = {
            'S': (0.2,),
            'G': (1.0,),
            'F': (0.6,),
            'H': (0.0,),
            'P': (0.4,)}

        self._action_gen = FeatureGeneratorSet(FeatureGenerator.categorical(
            name='move', categories=moves))

        self._default_actions = tuple(self._action_gen.generate_all())

        self.state.add_definition(
            'full_map', ('full_map', {}))
        self.state.add_definition(
            'neighborhood', ('neighborhood', {}))
        self.possible_actions.add_definition(
            'moves', self._actions, 'full_map')

        self.reset()

    @staticmethod
    def _locate(_map: List[List[Any]], element: Any) -> Tuple[int, int]:
        row = [element in m_i for m_i in _map].index(True)
        col = _map[row].index(element)
        return (row, col)

    def _actions(self, board: Feature) -> FeatureGeneratorType:
        return self._action_gen.make_generator()

    def is_terminated(self, _id: Optional[int] = None) -> bool:
        '''Return True if the player get to the goal or falls into a hole.'''
        if self._init_board:
            return self._init_board[self._board.index('P')] in ('H', 'G')
        return self._player_location == self._goal

    def _default_reward_definition(
            self, _id: Optional[int] = None) -> float:
        if self._player_location == self._goal:
            return 10.0
        if (
                self._init_board and
                self._init_board[self._board.index('P')] == 'H'):
            return -1.0

        return -0.1

    def _take_effect(
            self, action: FeatureSet, _id: int) -> FeatureSet:
        '''
        Move according to the action.

        Arguments
        ---------
            _id: ID of the player.
            action: the location in which the piece is set. Can be either
            in index format or row column format.
        '''
        row, column = self._player_location
        max_row = self._dim[0] - 1
        max_column = self._dim[1] - 1
        MNKBoard.clear_square(self, row=row, column=column)

        a = action['move'].value
        temp = (
            row - (a in ['U', 'UR', 'UL']) + (a in ['D', 'DR', 'DL']),
            column - (a in ['L', 'UL', 'DL']) + (a in ['R', 'UR', 'DR'])
        )

        self._player_location = (
            min(max(temp[0], 0), max_row),
            min(max(temp[1], 0), max_column)
        )

        if not self._terminate_on_hole and self.get_square(
                row=self._player_location[0],
                column=self._player_location[1]) == 'H':
            self._player_location = self._start

        MNKBoard.set_piece(
            self, player=_id,
            row=self._player_location[0],
            column=self._player_location[1])

        return action

    def reset(self):
        '''Clear the board and update board_status.'''
        Subject.reset(self)
        MNKBoard.reset(self)

        self._player_location = self._start
        MNKBoard.set_piece(
            self, player=1,
            row=self._player_location[0],
            column=self._player_location[1])

    def _sub_comp_full_map(
            self, _id: int, **kwargs: Any) -> Feature:
        board_list: Tuple[str, ...] = tuple(self.get_board())  # type: ignore

        return self._board_gen(board_list)

    def _sub_comp_neighborhood(
            self, _id: int, **kwargs: Any) -> Feature:
        r, c = self._player_location
        board_list = ['F'] * 9
        # tl, tc, tr, _l, _c, _r, bl, bc, br
        if r > 0:
            if c > 0:
                board_list[0] = self.get_square(row=r-1, column=c-1)
            board_list[1] = self.get_square(row=r-1, column=c)
            if c < self._n - 1:
                board_list[2] = self.get_square(row=r-1, column=c+1)

        if c > 0:
            board_list[3] = self.get_square(row=r, column=c-1)
        board_list[4] = self.get_square(row=r, column=c)
        if c < self._n - 1:
            board_list[5] = self.get_square(row=r, column=c+1)

        if r < self._m - 1:
            if c > 0:
                board_list[6] = self.get_square(row=r+1, column=c-1)
            board_list[7] = self.get_square(row=r+1, column=c)
            if c < self._n - 1:
                board_list[8] = self.get_square(row=r+1, column=c+1)

        return self._board_gen(tuple(board_list))


if __name__ == '__main__':
    board = FrozenLake()
    _ = board.register('P1')
    while board.reward('default') != 1:
        action_gen: FeatureGeneratorType = \
            board.possible_actions('moves')  # type: ignore
        next(action_gen)
        my_action = choice(tuple(action_gen.send('return feature')))
        board.take_effect(my_action, 1)
        print(my_action.value)
        print(f'{board}')
