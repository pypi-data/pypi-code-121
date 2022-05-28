# -*- coding: utf-8 -*-
# type: ignore
'''
Snake class
===========

This `subject` class emulates a single player snake game. 


'''

import curses
from curses import KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_UP
from random import randint

from ..valueset import ValueSet
from .mnkboard import MNKBoard
from .mnkgame import MNKGame
from .subject import Subject


def main():
    pass


class Snake(MNKBoard, Subject):
    '''
    Create a single player snake game.

    Attributes
    ----------
        is_terminated: whether the game finished or not.
        possible_actions: a list of possible actions.

    Methods
    -------
        take_effect: set a piece of the specified player on the specified square of the board.
        reset: clear the board.
    '''
    def __init__(self, **kwargs):
        '''
        Initialize an instance of snake game.

        Arguments
        ---------
            m: number of rows (default=10)
            n: number of columns (default=10)
        '''
        self._m = 10
        self._n = 10
        self.set_params(**kwargs)
        super().__init__(**kwargs)
        self.reset()

    @property
    def is_terminated(self):
        '''Return True if the game is finished.'''
        return (self._snake[0] in self._snake[1:])
    
    @property
    def possible_actions(self):
        '''Return the moves as ValueSet (left, none, right).'''
        return ValueSet(['left', 'none', 'right'])

    def take_effect(self, action, _id=None):
        '''
        Move the snake on the board.

        Arguments
        ---------
            _id: ID of the player. (Not used in the code)
            action: one of three possible actions: left, none, right.
        ''' 
        self._win.border(0)
        self._win.addstr(0, 2, 'Score : ' + str(self._score) + ' ')                # Printing 'Score' and
        self._win.addstr(0, 27, ' SNAKE ')                                   # 'SNAKE' strings
        self._win.timeout(150 - int(len(self._snake)/5 + len(self._snake)/10)%120)          # Increases the speed of Snake as its length increases
        
        # prevKey = self._key                                                  # Previous key pressed
        _ = self._win.getch()
        if action == 'left':
            if self._key == KEY_LEFT:
                self._key = KEY_DOWN
            elif self._key == KEY_DOWN:
                self._key = KEY_RIGHT
            elif self._key == KEY_RIGHT:
                self._key = KEY_UP
            elif self._key == KEY_UP:
                self._key = KEY_LEFT
        elif action == 'right':
            if self._key == KEY_LEFT:
                self._key = KEY_UP
            elif self._key == KEY_UP:
                self._key = KEY_RIGHT
            elif self._key == KEY_RIGHT:
                self._key = KEY_DOWN
            elif self._key == KEY_DOWN:
                self._key = KEY_LEFT

        # if key == ord(' '):                                            # If SPACE BAR is pressed, wait for another
        #     key = -1                                                   # one (Pause/Resume)
        #     while key != ord(' '):
        #         key = win.getch()
        #     key = prevKey
        #     continue

        # if key not in [KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN, 27]:     # If an invalid key is pressed
        #     key = prevKey

        # Calculates the new coordinates of the head of the snake. NOTE: len(snake) increases.
        # This is taken care of later at [1].
        self._snake.insert(0, [self._snake[0][0] + (self._key == KEY_DOWN and 1) + (self._key == KEY_UP and -1), self._snake[0][1] + (self._key == KEY_LEFT and -1) + (self._key == KEY_RIGHT and 1)])
        if self._snake[0][0] == 0: self._snake[0][0] = self._m - 2
        if self._snake[0][1] == 0: self._snake[0][1] = self._n - 2
        if self._snake[0][0] == self._m: self._snake[0][0] = 1
        if self._snake[0][1] == self._n: self._snake[0][1] = 1
        # print(self._snake[0][0], self._snake[0][1], (self._snake[0][0] * 6 + self._snake[0][1]))
        self.set_piece(1, row=self._snake[0][0], column=self._snake[0][1])
        if self._snake[0] == self._food:                                            # When snake eats the food
            self._food = []
            self._score += 1
            while self._food == []:
                self._food = [randint(1, self._m-2), randint(1, self._n-2)]                 # Calculating next food's coordinates
                if self._food in self._snake: self._food = []
            self._win.addch(self._food[0], self._food[1], '*')
            self.set_piece(2, row=self._food[0], column=self._food[1])
        else:
            last = self._snake.pop()                                          # [1] If it does not eat the food, length decreases
            self._win.addch(last[0], last[1], ' ')
            self.clear_square(row=last[0], column=last[1])
        self._win.addch(self._snake[0][0], self._snake[0][1], '#')
        return self._score

    def reset(self):
        '''Clear the board, reset the snake and the fruit and update board_status.'''
        MNKBoard.reset(self)
        curses.initscr()
        self._win = curses.newwin(20, 60, 0, 0)
        self._win.keypad(1)
        curses.noecho()
        curses.curs_set(0)
        self._win.border(0)
        self._win.nodelay(1)
        self._key = KEY_RIGHT                                                    # Initializing values
        self._score = 0
        self._snake = [[self._m // 2, self._n // 2 + 1],
                       [self._m // 2, self._n // 2],
                       [self._m // 2, self._n // 2 - 1]]                                     # Initial snake co-ordinates
        self._food = [self._m // 2 + 1, self._n // 2]                                                     # First food co-ordinates
        self._win.addch(self._food[0], self._food[1], '*')                       # Prints the food
        super().__init__(self)
        for location in self._snake:
            self.set_piece(1, row=location[0], column=location[1])
        self.set_piece(2, row=self._food[0], column=self._food[1])

    def __repr__(self):
        return 'Snake'

if __name__ == '__main__':
    main()
