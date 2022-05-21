from sudoku.core.iterators import *

from copy import deepcopy
import itertools

class sudoku_grid:
    """
    Classe permettant d'interagir avec une grille de sudoku.
    """

    """
    Représente comment la grille de sudoku est représentée en format
    caractères. Chaque `0` correspond à une valeur qui sera remplacé par la
    valeur appropriée.
    """

    str_grid = \
"""
+-----------+-----------+-----------+
| 0   0   0 | 0   0   0 | 0   0   0 |
|           |           |           |
| 0   0   0 | 0   0   0 | 0   0   0 |
|           |           |           |
| 0   0   0 | 0   0   0 | 0   0   0 |
+-----------+-----------+-----------+
| 0   0   0 | 0   0   0 | 0   0   0 |
|           |           |           |
| 0   0   0 | 0   0   0 | 0   0   0 |
|           |           |           |
| 0   0   0 | 0   0   0 | 0   0   0 |
+-----------+-----------+-----------+
| 0   0   0 | 0   0   0 | 0   0   0 |
|           |           |           |
| 0   0   0 | 0   0   0 | 0   0   0 |
|           |           |           |
| 0   0   0 | 0   0   0 | 0   0   0 |
+-----------+-----------+-----------+
"""

    def __init__(self, grid: list[int] = [0] * 81) -> None:
        """
        Initialise `self`.

        Arguments :

            grid - Tableau représentant la grille de sudoku décrite par sens de
            lecture (de gauche à droite et de haut en bas). Ce tableau ne doit
            contenir que des valeurs comprises entre 1 et 9 (si la case est
            remplie), ou 0 (si la case est vide). Par défaut, cet argument vaut
            la valeur correspondant à une grille vide (ne contenant que des
            zéros).
        """

        for i in grid:
            if i > 9:
                raise ValueError(
                    "A sudoku grid must contain only numbers between 1 and " +
                    "9, or 0 (if the corresponding cell is empty)."
                )

        self.grid = grid

    def __str__(self) -> str:
        """
        Convertie l'objet en une chaîne de caractère afin d'ếtre, entre autres,
        imprimable en console.
        """

        ret     = ""
        grid_it = iter(self.grid)

        for i in self.str_grid:
            if i == "0":
                ret += str(next(grid_it))
            else:
                ret += i

        return ret

    def get_column_iter(self, n: int) -> column_iterator:
        """
        Retourne le `column_iterator` dont l'itérateur contenu dans cette
        instance pointe vers le premier élément de la colonne contenant
        la `n`-ième case.

        Argument :

            n - Indice de la case dont on veut connaître la colonne.
        """

        return column_iterator(itertools.islice(iter(self.grid), n % 9, None))

    def get_row_iter(self, n: int) -> row_iterator:
        """
        Retourne le `row_iterator` dont l'itérateur contenu dans cette instance
        pointe vers le premier élément de la ligne contenant la `n`-ième case.

        Argument :

            n - Indice de la case dont on veut connaître la ligne.
        """

        return row_iterator(
            itertools.islice(iter(self.grid), (n // 9) * 9, None)
        )

    def get_square_iter(self, n: int) -> square_iterator:
        """
        Retourne le `square_iterator` dont l'itérateur contenu dans cette
        instance pointe vers le premier élément du carré contenant la `n`-ième
        case.

        Argument :

            n - Indice de la case dont on veut connaître le carré.
        """

        return square_iterator(
            itertools.islice(
                iter(self.grid), (n // 27) * 27 + ((n % 9) // 3) * 3, None
            )
        )

    def is_in_column(self, value: int, i: int) -> bool:
        """
        Vérifie si `value` est contenu dans la colonne contenant la `i`-ième
        case.

        Argument :
            value - Valeur test.

            i - Indice correspondant à la position de la valeur test dans la
            grille.
        """

        if value > 9:
            return False
        else:
            return value in self.get_column_iter(i)

    def is_in_row(self, value: int, i: int) -> bool:
        """
        Vérifie si `value` est contenu dans la ligne contenant la `i`-ième
        case.

        Argument :
            value - Valeur test.

            i - Indice correspondant à la position de la valeur test dans la
            grille.
        """

        if value > 9:
            return False
        else:
            return value in self.get_row_iter(i)

    def is_in_square(self, value: int, i: int) -> bool:
        """
        Vérifie si `value` est contenu dans le carré contenant la `i`-ième
        case.

        Argument :
            value - Valeur test.

            i - Indice correspondant à la position de la valeur test dans la
            grille.
        """

        if value > 9:
            return False
        else:
            return value in self.get_square_iter(i)

    def could_be_in(self, value: int, i: int) -> bool:
        """
        Vérifie si `value` pourrait se situer dans la `i`-ième case.

        Argument :
            value - Valeur test.

            i - Indice correspondant à la position de la valeur test dans la
            grille.
        """

        return not self.is_in_column(value, i) and \
            not self.is_in_row(value, i) and \
            not self.is_in_square(value, i)

    def is_empty(self) -> bool:
        """
        Vérifie si la grille est vide.
        """

        for i in self.grid:
            if i != 0:
                return False

        return True

    def is_finished(self) -> bool:
        """
        Vérifie si la grille est complétée et valide.
        """

        for val in range(1, 10):
            for i in range(9):
                if not self.is_in_column(val, i):
                    return False

                if not self.is_in_row(val, i):
                    return False

                if not self.is_in_square(val, 27 * (i // 3) + 3 * (i % 3)):
                    return False

        return True

    def get_empty_cells(self) -> list[int]:
        """
        Retourne la liste des indices des cases vides.
        """

        ret = []

        for i in range(len(self.grid)):
            if self.grid[i] == 0:
                ret.append(i)

        return ret

    def get_number_of_empty_cells(self) -> int:
        """
        Retourne le nombre de cases vides.
        """

        counter = 0

        for i in self.grid:
            if i == 0:
                counter += 1

        return counter

    def solve(self) -> None:
        """
        Résout la grille.
        """

        """
        Fait une copie de l'objet courrant afin de ne pas le corrompre en cas
        d'échec de la résolution (si la grille est invalide).
        """
        tmp = self

        """
        Pour chaque case vide, on associe la liste des différentes valeurs
        individuellement possibles.
        """

        allowed_values = {}

        for i in tmp.get_empty_cells():
            for val in range(1, 10):
                if tmp.could_be_in(val, i):
                    allowed_values.setdefault(i, []).append(val)

        allowed_values = \
            {k: v for k, v in sorted(allowed_values.items(), key = lambda a: len(a[1]))}

        """
        On initialise une liste dont chaque élement suit le schéma suivant :

        ```
        [indice dans la grille, possibilité sélectionnée, possibilité de début]
        ```
        """

        selected_cells = []

        for (i, allowed) in allowed_values.items():
            selected_cells.append([i, iter(allowed), iter(allowed)])

        i = 0

        """
        Algorithme de retour sur trace.
        """
        while i != len(selected_cells):
            grid_index, _, allowed_begin = selected_cells[i]

            try:
                val = next(selected_cells[i][1])

                """
                On vérifie que la valeur sélectionnée est bien valide.
                """
                if tmp.could_be_in(val, grid_index):
                    tmp.grid[grid_index] = val

                    i += 1
            except StopIteration:
                """
                Le précédant appel de `next()` a échoué : il ne reste plus
                d'autre possibilité pour cette case dans cette configuration :
                au moins une case précédente est incorrecte.
                """

                if i == 0:
                    """
                    On est déjà à la première case vide : on ne peut pas
                    retourner sur sa trace (la grille est invalide).
                    """

                    raise RuntimeError("The sudoku has no solution.")
                else:
                    """
                    On retourne sur sa trace.
                    """

                    selected_cells[i][1] = deepcopy(allowed_begin)
                    tmp.grid[grid_index] = 0

                    i -= 1

        """
        On vérifie que la grille est bien résolue.
        """

        if not tmp.is_finished():
            raise RuntimeError("The sudoku has no solution.")

        self = tmp
