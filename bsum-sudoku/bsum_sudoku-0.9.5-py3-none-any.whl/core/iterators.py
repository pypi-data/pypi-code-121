from collections.abc import Iterator
from typing import TypeVar

__all__ = ["column_iterator", "row_iterator", "square_iterator"]

T = TypeVar("T")

class column_iterator:
    """
    Une classe permettant l'itération sur une colonne d'une grille de sudoku,
    cette dernière étant représentée comme un tableau à une dimension.
    """

    def __init__(self, iter: Iterator[T], counter: int = -1) -> None:
        """
        Initialise `self`.

        Arguments :

            iter - Un itérateur de la grille de sudoku.

            counter - Spécifie que `iter` pointe vers le `counter`-ième élément
            de la colonne.
        """

        self.iter    = iter
        self.counter = counter

    def __iter__(self: "column_iterator") -> "column_iterator":
        return self

    def __next__(self) -> T:
        if self.counter != -1:
            for _ in range(8):
                next(self.iter)
        elif self.counter == 8:
            raise StopIteration

        self.counter += 1

        return next(self.iter)

class row_iterator:
    """
    Une classe permettant l'itération sur une ligne d'une grille de sudoku,
    cette dernière étant représentée comme un tableau à une dimension.
    """

    def __init__(self, iter: Iterator[T], counter: int = -1) -> None:
        """
        Initialise `self`.

        Arguments :

            iter - Un itérateur de la grille de sudoku.

            counter - Spécifie que `iter` pointe vers le `counter`-ième élément
            de la ligne.
        """

        self.iter    = iter
        self.counter = counter

    def __iter__(self: "row_iterator") -> "row_iterator":
        return self

    def __next__(self) -> T:
        if self.counter == 8:
            raise StopIteration

        self.counter += 1

        return next(self.iter)

class square_iterator:
    """
    Une classe permettant l'itération sur un carré d'une grille de sudoku,
    cette dernière étant représentée comme un tableau à une dimension.
    """

    def __init__(self, iter: Iterator[T], counter: int = -1) -> None:
        """
        Initialise `self`.

        Arguments :

            iter - Un itérateur de la grille de sudoku.

            counter - Spécifie que `iter` pointe vers le `counter`-ième élément
            du carré.
        """

        self.iter    = iter
        self.counter = counter

    def __iter__(self: "square_iterator") -> "square_iterator":
        return self

    def __next__(self) -> T:
        if self.counter == 8:
            raise StopIteration

        self.counter += 1

        if ((self.counter % 3) == 0) and (self.counter != 0):
            for _ in range(6):
                next(self.iter)

        return next(self.iter)
