# -*- coding: utf-8 -*-
'''
MNKBoard class
==============

This class creates a board for players to play the mnk game.
'''

import math
from typing import (Any, Dict, Generic, Iterator, List, Optional, Tuple,
                    TypeVar, Union, cast, overload)

from reil.datatypes.feature import FeatureSet, FeatureGenerator

T = TypeVar('T')


class MNKBoard(Generic[T]):
    '''
    Provide an m-by-n board to play.
    '''

    def __init__(
            self, m: int = 3, n: int = 3, k: int = 3,
            player_names: Optional[Dict[int, T]] = None, players: int = 2,
            blank_val: T = 0, init_board: Optional[List[T]] = None,
            can_recapture: bool = True, **kwargs: Any):
        '''
        Arguments
        ---------
        m:
            The number of rows.

        n:
            The number of columns.

        k:
            The winning criterion, i.e. the number of cells in one row, column,
            or diagonal that a player needs to capture to win the game.

        players:
            The number of players.

        can_recapture:
            Whether a piece can be put on an occupied square
        '''
        self._m = m
        self._n = n
        self._k = k
        self._players = players or len(player_names or {})
        self._can_recapture = can_recapture

        self._blank_val = blank_val
        self._init_board = init_board
        self._player_names = (
            player_names or {i: cast(T, i) for i in range(1, players+1)})

        self._board_state_gen = FeatureGenerator.categorical(
            name='state', categories=tuple(
                list(self._player_names.values()) + [self._blank_val]))

        self.reset()

    @overload
    def set_piece(self, player: int, index: int) -> None:
        '''
        Set a piece for a player.

        Arguments
        ---------
        player:
            ID of the player whose piece will be set on the board.

        index:
            Where to put the piece. Index starts from 0 and assumes the board
            to be a list.

        Raises
        ------
        ValueError:
            Wrong player ID.

        ValueError:
            index is out of range.
        '''
        ...

    @overload
    def set_piece(self, player: int, row: int, column: int) -> None:
        '''
        Set a piece for a player.

        Arguments
        ---------
        player:
            ID of the player whose piece will be set on the board.

        row:
            The row on which the piece should be placed.

        column:
            The column on which the piece should be placed.

        Raises
        ------
        ValueError:
            Wrong player ID.

        ValueError:
            index is out of range.
        '''
        ...

    def set_piece(  # type: ignore
            self, player: int, index: Optional[int] = None,
            row: Optional[int] = None, column: Optional[int] = None
            ) -> None:
        '''
        Set a piece for a player.

        Arguments
        ---------
        player:
            ID of the player whose piece will be set on the board.

        row:
            The row on which the piece should be placed.

        column:
            The column on which the piece should be placed.

        index:
            Where to put the piece. Index starts from 0 and assumes the board
            to be a list.

        Raises
        ------
        ValueError:
            Wrong player ID.

        ValueError:
            index is out of range.

        Notes
        -----
        Either `index` or `row` and `column` should be used. If both are used,
        `row` and `column` is used.
        '''
        if player <= 0 or player > self._players:
            raise ValueError('player not found.')

        if row is None or column is None:
            if index is None:
                raise ValueError('No row-column pair or index found.')
            else:
                _index = index
        else:
            _index = row * self._n + column

        if self._board[_index] and not self._can_recapture:
            raise ValueError('The square is already occupied.')
        self._board[_index] = self._player_names[player]

    @overload
    def get_square(self, index: int) -> T:
        '''
        Get the piece on a given position.

        Arguments
        ---------
        index:
            Where to loop up on the board. Index starts from 0 and assumes
            the board to be a list.

        Raises
        ------
        ValueError:
            index is out of range.
        '''
        ...

    @overload
    def get_square(self, row: int, column: int) -> T:
        '''
        Get the piece on a given position.

        Arguments
        ---------
        row:
            The row from which the piece should be looked up.

        column:
            The column from which the piece should be looked up.

        Raises
        ------

        ValueError:
            index is out of range.
        '''
        ...

    def get_square(  # type: ignore
            self, index: Optional[int] = None,
            row: Optional[int] = None, column: Optional[int] = None
            ) -> T:
        '''
        Get the piece on a given position.

        Arguments
        ---------
        row:
            The row from which the piece should be looked up.

        column:
            The column from which the piece should be looked up.

        index:
            Where to loop up on the board. Index starts from 0 and assumes
            the board to be a list.

        Raises
        ------
        ValueError:
            index is out of range.

        Notes
        -----
        Either `index` or `row` and `column` should be used. If both are used,
        `row` and `column` is used.
        '''
        if row is None or column is None:
            if index is None:
                raise ValueError('No row-column pair or index found.')
            else:
                _index = index
        else:
            _index = row * self._n + column

        return self._board[_index]

    @overload
    def clear_square(self, index: int) -> None:
        '''
        Set a piece for a player.

        Arguments
        ---------
        index:
            index to be cleared. Index starts from 0 and assumes the board
            to be a list.

        Raises
        ------
        ValueError:
            index is out of range.
        '''
        ...

    @overload
    def clear_square(self, row: int, column: int) -> None:
        '''
        Set a piece for a player.

        Arguments
        ---------
        row:
            The row on which a cell should be cleared.

        column:
            The column on which a cell should be cleared.

        Raises
        ------
        ValueError:
            index is out of range.
        '''
        ...

    def clear_square(  # type: ignore
            self, index: Optional[int] = None,
            row: Optional[int] = None, column: Optional[int] = None) -> None:
        '''
        Set a piece for a player.

        Arguments
        ---------
        row:
            The row on which a cell should be cleared.

        column:
            The column on which a cell should be cleared.

        index:
            index to be cleared. Index starts from 0 and assumes the board
            to be a list.

        Raises
        ------
        ValueError:
            index is out of range.

        Notes
        -----
        Either `index` or `row` and `column` should be used. If both are used,
        `row` and `column` is used.
        '''

        if row is None or column is None:
            if index is None:
                raise ValueError('No row-column pair or index found.')
            else:
                _index = index
        else:
            _index = row * self._n + column

        if self._init_board:
            val = self._init_board[_index]
        else:
            val = self._blank_val

        self._board[_index] = val

    @property
    def board_state(self):
        ''' Return the state of the board as a FeatureSet.'''
        return FeatureSet(self._board_state_gen(tuple(self._board)))

    def get_board(
            self, as_list: bool = True) -> Union[List[T], List[List[T]]]:
        '''
        Return the board.

        Arguments
        ---------
        as_list:
            Whether to return the board as a list or a matrix.

        Returns
        -------
        :
            The board as a list or a 2D matrix.
        '''
        if as_list:
            return self._board
        else:
            return self.list_to_matrix(self._board, self._m, self._n)

    def get_action_set(
            self, as_list: bool = True
    ) -> Union[Iterator[int], Iterator[Tuple[int, int]]]:
        '''
        Return a list of indexes of empty squares.

        Arguments
        ---------
        as_list:
            Whether to return the board as a list or a matrix.
        '''
        index = (
            i for i in range(self._m*self._n)
            if self._board[i] == self._blank_val)
        for action in index:
            if as_list:
                yield action
            else:
                yield (action // self._n, action % self._n)

    def reset(self) -> None:
        '''Clear the board.'''
        if self._init_board:
            self._board = [x for x in self._init_board]
        else:
            self._board = [self._blank_val]*(self._m*self._n)

    def __str__(self):
        '''Return a printable format string of the board.'''
        return ('\n'.join(
            [''.join([f'{item:4}' for item in row])
             for row in self.list_to_matrix(self._board, self._m, self._n)]))

    @staticmethod
    def list_to_matrix(
            board: List[T],
            m: int, n: Optional[int] = None) -> List[List[T]]:
        '''
        Covert a list to a 2D matrix.

        Arguments
        ---------
        board:
            The board to be converted.

        m:
            The number of rows.

        n:
            The number of columns. If omitted, it will be infered from the
            `board` size and `m`.
        '''
        _n = n or math.ceil(len(board) / m)

        return [board[row*_n:(row+1)*_n] for row in range(m)]

    def __repr__(self):
        return (self.__class__.__qualname__ + f', {self._m} x {self._n} board,'
                f' {self._k} on a line wins, {self._players} players')


if __name__ == '__main__':
    # create a board and set piece for each player and print the board
    board = MNKBoard(
        m=3, n=3, k=3, players=3, player_names={1: 'A', 2: 'B', 3: 'C'},
        blank_val=' ')
    board.set_piece(1, row=0, column=0)
    board.set_piece(2, index=4)
    board.set_piece(3, index=8)
    print(f'{board}')
