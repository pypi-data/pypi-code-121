"""Dellacherie agent.
"""

from copy import deepcopy

import numpy as np
from gym_simplifiedtetris.envs._simplified_tetris_engine import _SimplifiedTetrisEngine


class HeuristicAgent(object):
    """An agent that selects actions according to a heuristic."""

    WEIGHTS = np.array([-1, 1, -1, -1, -4, -1], dtype="double")

    def predict(self, env: _SimplifiedTetrisEngine) -> int:
        """Return the action yielding the largest heuristic score.

        Ties are separated using a priority rating, which is based on the translation and rotation.

        :param env: environment that the agent resides in.
        :return: action with the largest rating; ties are separated based on the priority.
        """
        dellacherie_scores = self._get_dellacherie_scores(env)
        return np.argmax(dellacherie_scores)

    def _get_dellacherie_scores(self, env: _SimplifiedTetrisEngine) -> np.array:
        """Compute and return the Dellacherie feature values.

        :param env: environment that the agent resides in.
        :return: Dellacherie feature values.
        """
        scores = np.empty((env._engine._num_actions), dtype="double")

        for action, (translation, rotation) in env._engine._all_available_actions[
            env._engine._piece._id
        ].items():
            old_grid = deepcopy(env._engine._grid)
            old_anchor = deepcopy(env._engine._anchor)
            old_colour_grid = deepcopy(env._engine._colour_grid)

            env._engine._rotate_piece(rotation)

            env._engine._anchor = [translation, 0]

            env._engine._hard_drop()
            env._engine._update_grid(True)
            env._engine._clear_rows()

            feature_values = np.empty((6), dtype="double")
            for idx, feature_func in enumerate(self._get_dellacherie_funcs()):
                feature_values[idx] = feature_func(env)

            scores[action] = np.dot(feature_values, self.WEIGHTS)

            env._engine._update_grid(False)

            env._engine._anchor = deepcopy(old_anchor)
            env._engine._grid = deepcopy(old_grid)
            env._engine._colour_grid = deepcopy(old_colour_grid)

        max_idx = np.argwhere(scores == np.amax(scores)).flatten()
        is_a_tie = len(max_idx) > 1

        # Resort to the priorities when there is a tie.
        return self._get_priorities(max_idx, env) if is_a_tie else scores

    def _get_priorities(
        self, max_indices: np.array, env: _SimplifiedTetrisEngine
    ) -> np.array:
        """Compute and return the priorities of the available actions.

        :param max_indices: actions with the maximum ratings.
        :param env: environment that the agent resides in.
        :return: priorities.
        """
        priorities = np.zeros((env._engine._num_actions), dtype="double")

        for action in max_indices:
            translation, rotation = env._engine._all_available_actions[
                env._engine._piece._id
            ][action]
            x_spawn_pos = env._engine._width / 2 + 1
            priorities[action] += 100 * abs(translation - x_spawn_pos)

            if translation < x_spawn_pos:
                priorities[action] += 10

            priorities[action] -= rotation / 90

            # Ensure that the priority of the best actions is never negative.
            priorities[action] += 5  # 5 is always greater than rotation / 90.

        return priorities

    def _get_dellacherie_funcs(self) -> list:
        """Return the Dellacherie feature functions.

        :return: Dellacherie feature functions.
        """
        return [
            self._get_landing_height,
            self._get_eroded_cells,
            self._get_row_transitions,
            self._get_column_transitions,
            self._get_holes,
            self._get_cumulative_wells,
        ]

    def _get_landing_height(self, env: _SimplifiedTetrisEngine) -> int:
        """Compute the landing height and return it.

        Landing height = the midpoint of the last piece to be placed.

        :param env: environment that the agent resides in.
        :return: landing height.
        """
        return (
            env._engine._last_move_info["landing_height"]
            if "landing_height" in env._engine._last_move_info
            else 0
        )

    def _get_eroded_cells(self, env: _SimplifiedTetrisEngine) -> int:
        """Return the eroded cells value. Num. eroded cells = number of rows cleared x number of blocks removed that were added to the grid by the last action.

        :param env: environment that the agent resides in.
        :return: eroded cells.
        """
        return (
            env._engine._last_move_info["num_rows_cleared"]
            * env._engine._last_move_info["eliminated_num_blocks"]
            if "num_rows_cleared" in env._engine._last_move_info
            else 0
        )

    def _get_row_transitions(self, env: _SimplifiedTetrisEngine) -> float:
        """Return the row transitions value.

        Row transitions = Number of transitions from empty to full cells (or vice versa), examining each row one at a time.

        Author: Ben Schofield
        Source: https://github.com/Benjscho/gym-mdptetris/blob/1a47edc33330deb638a03275e484c3e26932d802/gym_mdptetris/envs/feature_functions.py#L45

        :param env: environment that the agent resides in.
        :return: row transitions.
        """
        # Adds a column either side.
        grid = np.ones((env._engine._width + 2, env._engine._height), dtype="bool")

        grid[1:-1, :] = env._engine._grid.copy()
        return np.diff(grid.T).sum()

    def _get_column_transitions(self, env: _SimplifiedTetrisEngine) -> float:
        """Return the column transitions value.

        Column transitions = Number of transitions from empty to full (or vice versa), examining each column one at a time.

        Author: Ben Schofield
        Source: https://github.com/Benjscho/gym-mdptetris/blob/1a47edc33330deb638a03275e484c3e26932d802/gym_mdptetris/envs/feature_functions.py#L60

        :param env: environment that the agent resides in.
        :return: column transitions.
        """
        # Adds a full row to the bottom.
        grid = np.ones((env._engine._width, env._engine._height + 1), dtype="bool")

        grid[:, :-1] = env._engine._grid.copy()
        return np.diff(grid).sum()

    def _get_holes(self, env: _SimplifiedTetrisEngine) -> int:
        """Compute the number of holes present in the current grid and return it.

        A hole is an empty cell with at least one full cell above it in the same column.

        :param env: environment that the agent resides in.
        :return: value of the feature holes.
        """
        return np.count_nonzero((env._engine._grid).cumsum(axis=1) * ~env._engine._grid)

    def _get_cumulative_wells(self, env: _SimplifiedTetrisEngine) -> int:
        """Compute the cumulative wells value and return it.

        Cumulative wells is defined here:
        https://arxiv.org/abs/1905.01652.  For each well, find the depth of
        the well, d(w), then calculate the sum of i from i=1 to d(w).  Lastly,
        sum the well sums.  A block is part of a well if the cells directly on
        either side are full and the block can be reached from above (i.e., there are no full cells directly above it).

        Attribution: Ben Schofield

        :param env: environment that the agent resides in.
        :return: cumulative wells value.
        """
        grid_ext = np.ones(
            (env._engine._width + 2, env._engine._height + 1), dtype="bool"
        )
        grid_ext[1:-1, 1:] = env._engine._grid[:, : env._engine._height]

        # This includes some cells that cannot be reached from above.
        potential_wells = (
            np.roll(grid_ext, 1, axis=0) & np.roll(grid_ext, -1, axis=0) & ~grid_ext
        )

        col_heights = np.zeros(env._engine._width + 2)
        col_heights[1:-1] = env._engine._height - np.argmax(env._engine._grid, axis=1)
        col_heights = np.where(col_heights == env._engine._height, 0, col_heights)

        x = np.linspace(1, env._engine._width + 2, env._engine._width + 2)
        y = np.linspace(env._engine._height + 1, 1, env._engine._height + 1)
        _, yv = np.meshgrid(x, y)

        # A cell that is part of a well must be above the playfield's outline, which consists of the highest full cells in each column.
        above_outline = (col_heights.reshape(-1, 1) < yv.T).astype(int)

        # Exclude the cells that cannot be reached from above by multiplying by 'above_outline'.
        cumulative_wells = np.sum(
            np.cumsum(potential_wells, axis=1) * above_outline,
        )

        return cumulative_wells
