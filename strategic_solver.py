"""
Strategic Human-like Sliding Puzzle Solver
===========================================
Translated from JavaScript implementation.
Strategy derived from: https://www.wikihow.com/Solve-Slide-Puzzles

Overall strategy:
- If puzzle is non-square, solve rows or columns first until remaining unsolved puzzle is square
- Alternate between solving rows and columns until it's a 2x2
- Solve rows top-down & columns left-right until reaching the goal's blank row/col
- If on the goal's blank row, start solving bottom-up. If on blank col, start solving right-left
- Once a tile is solved, never touch it again: each solved row/col reduces the problem space
"""

import heapq
import time
from enum import Enum
from typing import List, Tuple, Optional, Dict, Union
from copy import deepcopy


class PuzzleState:
    """State in puzzle search space (used by BFS solver)."""

    def __init__(self, board, empty_pos, g_cost, h_cost, parent=None, move=None):
        self.board = board
        self.empty_pos = empty_pos
        self.g_cost = g_cost
        self.h_cost = h_cost
        self.f_cost = h_cost  # Greedy: use only heuristic
        self.parent = parent
        self.move = move

    def __lt__(self, other):
        return self.f_cost < other.f_cost

    def __eq__(self, other):
        return self.board == other.board

    def __hash__(self):
        return hash(tuple(tuple(row) for row in self.board))


def manhattan_distance(board, size):
    """Calculate Manhattan distance heuristic."""
    distance = 0
    for i in range(size):
        for j in range(size):
            value = board[i][j]
            if value != 0:
                goal_row = (value - 1) // size
                goal_col = (value - 1) % size
                distance += abs(i - goal_row) + abs(j - goal_col)
    return distance


class Solvers(Enum):
    BFS = "BFS"
    HUMAN = "Human"


class Puzzle:
    """
    Puzzle class that mirrors the JS Puzzle functionality.
    Manages board state and provides slide operations.
    """

    def __init__(self, board: List[List[int]]):
        self.matrix = deepcopy(board)
        self.rows = len(board)
        self.cols = len(board[0]) if board else 0
        self.blank_row, self.blank_col = self._find_blank()
        self.solution_moves: List[str] = []

        # Progress tracking for strategic solving
        self.top_row_progress = 0
        self.left_col_progress = 0
        self.bot_row_progress = self.rows - 1
        self.right_col_progress = self.cols - 1

        self.row_in_progress = 0
        self.col_in_progress = 0
        self.row_progress_col = 0
        self.col_progress_row = 0
        self.solving_row_top_down = True
        self.solving_col_left_right = True
        self.solving_row = True

        # For coordinate-based move tracking
        self.coord_moves: List[Tuple[int, int]] = []

    def _find_blank(self) -> Tuple[int, int]:
        """Find the position of the blank (0) tile."""
        for i in range(self.rows):
            for j in range(self.cols):
                if self.matrix[i][j] == 0:
                    return (i, j)
        raise ValueError("No blank tile found")

    def can_slide_up(self) -> bool:
        """Can blank move up (stay within unsolved region)?"""
        return self.blank_row > self.top_row_progress

    def can_slide_down(self) -> bool:
        """Can blank move down (stay within unsolved region)?"""
        return self.blank_row < self.bot_row_progress

    def can_slide_left(self) -> bool:
        """Can blank move left (stay within unsolved region)?"""
        return self.blank_col > self.left_col_progress

    def can_slide_right(self) -> bool:
        """Can blank move right (stay within unsolved region)?"""
        return self.blank_col < self.right_col_progress

    def slide_up(self):
        """Blank moves up (row decreases). Tile above slides down into blank's old position."""
        if self.blank_row > 0:
            # Record the coordinate of the tile being moved (tile above blank)
            self.coord_moves.append((self.blank_row - 1, self.blank_col))
            self._swap(self.blank_row, self.blank_col, self.blank_row - 1, self.blank_col)
            self.blank_row -= 1

    def slide_down(self):
        """Blank moves down (row increases). Tile below slides up into blank's old position."""
        if self.blank_row < self.rows - 1:
            # Record the coordinate of the tile being moved (tile below blank)
            self.coord_moves.append((self.blank_row + 1, self.blank_col))
            self._swap(self.blank_row, self.blank_col, self.blank_row + 1, self.blank_col)
            self.blank_row += 1

    def slide_left(self):
        """Blank moves left (col decreases). Tile to left slides right into blank's old position."""
        if self.blank_col > 0:
            # Record the coordinate of the tile being moved (tile to left of blank)
            self.coord_moves.append((self.blank_row, self.blank_col - 1))
            self._swap(self.blank_row, self.blank_col, self.blank_row, self.blank_col - 1)
            self.blank_col -= 1

    def slide_right(self):
        """Blank moves right (col increases). Tile to right slides left into blank's old position."""
        if self.blank_col < self.cols - 1:
            # Record the coordinate of the tile being moved (tile to right of blank)
            self.coord_moves.append((self.blank_row, self.blank_col + 1))
            self._swap(self.blank_row, self.blank_col, self.blank_row, self.blank_col + 1)
            self.blank_col += 1

    def _swap(self, r1, c1, r2, c2):
        """Swap two positions in the matrix."""
        self.matrix[r1][c1], self.matrix[r2][c2] = self.matrix[r2][c2], self.matrix[r1][c1]

    def is_equal_to_puzzle(self, other: 'Puzzle') -> bool:
        """Check if this puzzle's matrix equals another's."""
        return self.matrix == other.matrix

    @staticmethod
    def get_matrix_mapping(matrix: List[List[int]]) -> Dict[int, Dict[str, int]]:
        """Create a mapping from tile values to their positions."""
        mapping = {}
        for i, row in enumerate(matrix):
            for j, val in enumerate(row):
                mapping[val] = {'row': i, 'col': j}
        return mapping

    @staticmethod
    def is_row_equal(goal_puzzle: 'Puzzle', puzzle: 'Puzzle', row: int) -> bool:
        """Check if a specific row matches between two puzzles."""
        return goal_puzzle.matrix[row] == puzzle.matrix[row]

    @staticmethod
    def is_col_equal(goal_puzzle: 'Puzzle', puzzle: 'Puzzle', col: int) -> bool:
        """Check if a specific column matches between two puzzles."""
        for row in range(puzzle.rows):
            if goal_puzzle.matrix[row][col] != puzzle.matrix[row][col]:
                return False
        return True


# ============================================================
# Helper functions for strategic solving
# ============================================================

def more_than_two_unsolved_rows(puzzle: Puzzle) -> bool:
    return puzzle.bot_row_progress + 1 - puzzle.top_row_progress > 2


def more_than_two_unsolved_cols(puzzle: Puzzle) -> bool:
    return puzzle.right_col_progress + 1 - puzzle.left_col_progress > 2


def more_unsolved_rows_than_cols(puzzle: Puzzle) -> bool:
    return (puzzle.bot_row_progress - puzzle.top_row_progress + 1 >=
            puzzle.right_col_progress + 1 - puzzle.left_col_progress)


def more_unsolved_cols_than_rows(puzzle: Puzzle) -> bool:
    return (puzzle.right_col_progress + 1 - puzzle.left_col_progress >
            puzzle.bot_row_progress + 1 - puzzle.top_row_progress)


def col_finished_and_not_in_goal_col(goal_puzzle: Puzzle, puzzle: Puzzle) -> bool:
    return (Puzzle.is_col_equal(goal_puzzle, puzzle, puzzle.col_in_progress) and
            puzzle.col_in_progress != goal_puzzle.blank_col)


def row_finished_and_not_in_goal_row(goal_puzzle: Puzzle, puzzle: Puzzle) -> bool:
    return (Puzzle.is_row_equal(goal_puzzle, puzzle, puzzle.row_in_progress) and
            puzzle.row_in_progress != goal_puzzle.blank_row)


def unsolved_puzzle_is_two_by_two(puzzle: Puzzle) -> bool:
    return (puzzle.bot_row_progress + 1 - puzzle.top_row_progress == 2 and
            puzzle.right_col_progress + 1 - puzzle.left_col_progress == 2)


def move_blank_to_col(puzzle: Puzzle, target_col: int):
    """Loop until blank is in the target column."""
    while puzzle.blank_col != target_col:
        if puzzle.blank_col < target_col:
            puzzle.slide_right()
        else:
            puzzle.slide_left()


def move_blank_to_row(puzzle: Puzzle, target_row: int):
    """Loop until blank is in the target row."""
    while puzzle.blank_row != target_row:
        if puzzle.blank_row < target_row:
            puzzle.slide_down()
        else:
            puzzle.slide_up()


def move_blank_left_or_right(puzzle: Puzzle):
    """Helper method for moving tile up/down when blank is in same col as tile."""
    if puzzle.blank_col == puzzle.right_col_progress:
        puzzle.slide_left()
    elif puzzle.blank_col == puzzle.left_col_progress:
        puzzle.slide_right()
    else:
        if puzzle.solving_col_left_right:
            puzzle.slide_right()
        else:
            puzzle.slide_left()


def move_blank_up_or_down(puzzle: Puzzle):
    """Helper method for moving tile left/right when blank is in same row as tile."""
    if puzzle.blank_row == puzzle.top_row_progress:
        puzzle.slide_down()
    elif puzzle.blank_row == puzzle.bot_row_progress:
        puzzle.slide_up()
    else:
        if puzzle.solving_row_top_down:
            puzzle.slide_down()
        else:
            puzzle.slide_up()


def move_tile_left(puzzle: Puzzle, tile: dict):
    """Move a tile one position to the left."""
    # Blank tile is to the right of value and in the same row
    if puzzle.blank_col > tile['col'] and tile['row'] == puzzle.blank_row:
        move_blank_up_or_down(puzzle)

    # Moving tile into its goal column on the left side
    if not puzzle.solving_row and puzzle.solving_col_left_right:
        # Tile is one right of our column in progress
        if tile['col'] == puzzle.col_in_progress + 1:
            # Tile not in last row
            if tile['row'] != puzzle.bot_row_progress:
                # Blank is to the right and or above our value
                if puzzle.blank_col >= tile['col'] and puzzle.blank_row < tile['row']:
                    move_blank_to_col(puzzle, tile['col'] + 1)
                    move_blank_to_row(puzzle, tile['row'] + 1)
            else:
                # If we're in the last row, we're moving the last two pieces
                move_blank_to_row(puzzle, tile['row'] - 1)
                move_blank_to_col(puzzle, tile['col'])

    # Move to left of tile
    move_blank_to_col(puzzle, tile['col'] - 1)
    move_blank_to_row(puzzle, tile['row'])
    puzzle.slide_right()


def move_tile_right(puzzle: Puzzle, tile: dict):
    """Move a tile one position to the right."""
    # Blank tile is to the left of value and in the same row
    if puzzle.blank_col < tile['col'] and tile['row'] == puzzle.blank_row:
        move_blank_up_or_down(puzzle)

    if puzzle.solving_row:
        if puzzle.solving_row_top_down:
            # Tile needs to go right, and our blank is in the row in progress
            if (puzzle.blank_row == puzzle.row_in_progress and
                    (puzzle.blank_row + 1 != tile['row'] or puzzle.blank_col != tile['col'])):
                if puzzle.can_slide_down():
                    puzzle.slide_down()
        else:
            # We're solving rows bottom to top
            if (puzzle.blank_row == puzzle.row_in_progress and
                    (puzzle.blank_row - 1 != tile['row'] or puzzle.blank_col != tile['col'])):
                if puzzle.can_slide_up():
                    puzzle.slide_up()
    else:
        # Solving column logic
        # Moving tile into its goal column on the right side
        if not puzzle.solving_col_left_right:
            # Tile is one left of our column in progress
            if tile['col'] == puzzle.col_in_progress - 1:
                # Tile not in last row
                if tile['row'] != puzzle.bot_row_progress:
                    # Blank is to the left and or above our value
                    if puzzle.blank_col <= tile['col'] and puzzle.blank_row < tile['row']:
                        move_blank_to_col(puzzle, tile['col'] - 1)
                        move_blank_to_row(puzzle, tile['row'] + 1)
                else:
                    # If we're in the last row, we're moving the last two pieces
                    move_blank_to_row(puzzle, tile['row'] - 1)
                    move_blank_to_col(puzzle, tile['col'])

    # Move to right of tile
    move_blank_to_col(puzzle, tile['col'] + 1)
    move_blank_to_row(puzzle, tile['row'])
    puzzle.slide_left()


def move_tile_up(puzzle: Puzzle, tile: dict):
    """Move a tile one position up."""
    # Moving tile into its goal row on the top
    if puzzle.solving_row and puzzle.solving_row_top_down:
        # Tile is in row below our in progress row
        if tile['row'] == puzzle.row_in_progress + 1:
            # Not in last column
            if tile['col'] != puzzle.right_col_progress:
                # Blank is to the left and/or under the value
                if puzzle.blank_col <= tile['col'] and puzzle.blank_row >= tile['row']:
                    move_blank_to_row(puzzle, tile['row'] + 1)
                    move_blank_to_col(puzzle, tile['col'] + 1)
            else:
                # If value is in last column, these are the last two pieces
                move_blank_to_col(puzzle, tile['col'] - 1)
                move_blank_to_row(puzzle, tile['row'])

    # If blank is under the value, move left or right
    if puzzle.blank_row > tile['row'] and puzzle.blank_col == tile['col']:
        move_blank_left_or_right(puzzle)

    # Move blank above the value and swap
    move_blank_to_row(puzzle, tile['row'] - 1)
    move_blank_to_col(puzzle, tile['col'])
    puzzle.slide_down()


def move_tile_down(puzzle: Puzzle, tile: dict):
    """Move a tile one position down."""
    # Solving column logic
    if not puzzle.solving_row:
        if puzzle.solving_col_left_right:
            # Tile needs to go down, blank is in the column in progress
            if (puzzle.blank_col == puzzle.col_in_progress and
                    (puzzle.blank_col + 1 != tile['col'] or puzzle.blank_row != tile['row'])):
                if puzzle.can_slide_right():
                    puzzle.slide_right()
        else:
            # We're solving columns right to left
            if (puzzle.blank_col == puzzle.col_in_progress and
                    (puzzle.blank_col - 1 != tile['col'] or puzzle.blank_row != tile['row'])):
                if puzzle.can_slide_left():
                    puzzle.slide_left()

    if puzzle.solving_row and not puzzle.solving_row_top_down:
        # Tile is in row above our in progress row
        if tile['row'] == puzzle.row_in_progress - 1:
            # Not in last column
            if tile['col'] != puzzle.right_col_progress:
                # Blank is to the left and/or above the value
                if puzzle.blank_col <= tile['col'] and puzzle.blank_row <= tile['row']:
                    move_blank_to_row(puzzle, tile['row'] - 1)
                    move_blank_to_col(puzzle, tile['col'] + 1)
            else:
                # If value is in last column, these are the last two pieces
                move_blank_to_col(puzzle, tile['col'] - 1)
                move_blank_to_row(puzzle, tile['row'])

    # If blank is above the value, move left or right
    if puzzle.blank_row < tile['row'] and puzzle.blank_col == tile['col']:
        move_blank_left_or_right(puzzle)

    # Move blank below the value and swap
    move_blank_to_row(puzzle, tile['row'] + 1)
    move_blank_to_col(puzzle, tile['col'])
    puzzle.slide_up()


def move_tile(puzzle: Puzzle, value: int, goal_row: int, goal_col: int):
    """
    Moves tile into its goal state with different logic depending if we're solving a row or column.
    When solving rows, position tile col first (left/right) and then row (up/down).
    When solving cols, position tile row first (up/down) and then col (left/right).
    """
    matrix_mapping = Puzzle.get_matrix_mapping(puzzle.matrix)
    value_row = matrix_mapping[value]['row']
    value_col = matrix_mapping[value]['col']

    # Tile already in its correct position
    if value_row == goal_row and value_col == goal_col:
        return

    tile = {
        'value': value,
        'row': value_row,
        'col': value_col,
        'goal_row': goal_row,
        'goal_col': goal_col
    }

    if puzzle.solving_row:
        # Left
        while tile['col'] > goal_col:
            move_tile_left(puzzle, tile)
            tile['col'] -= 1

        # Right
        while tile['col'] < goal_col:
            move_tile_right(puzzle, tile)
            tile['col'] += 1

        # Up
        while tile['row'] > goal_row:
            move_tile_up(puzzle, tile)
            tile['row'] -= 1

        # Down
        while tile['row'] < goal_row:
            move_tile_down(puzzle, tile)
            tile['row'] += 1
    else:
        # Solving column
        # Up
        while tile['row'] > goal_row:
            move_tile_up(puzzle, tile)
            tile['row'] -= 1

        # Down
        while tile['row'] < goal_row:
            move_tile_down(puzzle, tile)
            tile['row'] += 1

        # Left
        while tile['col'] > goal_col:
            move_tile_left(puzzle, tile)
            tile['col'] -= 1

        # Right
        while tile['col'] < goal_col:
            move_tile_right(puzzle, tile)
            tile['col'] += 1


def solve_puzzle_strategically(puzzle: Puzzle, goal_puzzle: Puzzle) -> Union[dict, bool]:
    """
    Main strategic solver function.
    Returns dict with solution info or False if failed.
    """
    start_time = time.time()

    # Check if puzzle is already solved
    if goal_puzzle.is_equal_to_puzzle(puzzle):
        return {
            'solution_puzzle': puzzle,
            'runtime_ms': 0,
            'coord_moves': [],
            'max_puzzles_in_memory': 1,
        }

    goal_matrix = goal_puzzle.matrix
    goal_mapping = Puzzle.get_matrix_mapping(goal_matrix)

    # Set state for effective bounds of the unsolved puzzle
    puzzle.top_row_progress = 0
    puzzle.left_col_progress = 0
    puzzle.bot_row_progress = puzzle.rows - 1
    puzzle.right_col_progress = puzzle.cols - 1

    # Start by solving rows top -> bottom and columns left -> right
    puzzle.row_in_progress = 0
    puzzle.col_in_progress = 0
    puzzle.row_progress_col = 0
    puzzle.col_progress_row = 0
    puzzle.solving_row_top_down = True
    puzzle.solving_col_left_right = True

    while not goal_puzzle.is_equal_to_puzzle(puzzle):

        # While we have more than 2 unsolved rows (stopping at 2x2)
        # If there are more or equal unsolved rows than columns, solve rows
        while more_than_two_unsolved_rows(puzzle) and more_unsolved_rows_than_cols(puzzle):
            puzzle.solving_row = True

            if row_finished_and_not_in_goal_row(goal_puzzle, puzzle):
                # Increment up or down depending on which way we're solving
                if puzzle.solving_row_top_down:
                    puzzle.top_row_progress += 1
                    puzzle.row_in_progress = puzzle.top_row_progress
                else:
                    puzzle.bot_row_progress -= 1
                    puzzle.row_in_progress = puzzle.bot_row_progress

                # Set progress to left corner of row
                puzzle.row_progress_col = 0
            else:
                if puzzle.solving_row_top_down:
                    # Once we've reached the goal state's blank row, start solving from the bottom
                    if puzzle.row_in_progress == goal_puzzle.blank_row:
                        puzzle.solving_row_top_down = False
                        puzzle.row_in_progress = puzzle.bot_row_progress
                    else:
                        puzzle.row_in_progress = puzzle.top_row_progress
                else:
                    puzzle.row_in_progress = puzzle.bot_row_progress

                row_iteration = 0
                target_value = goal_matrix[puzzle.row_in_progress][puzzle.row_progress_col]

                while not Puzzle.is_row_equal(goal_puzzle, puzzle, puzzle.row_in_progress):
                    # Guard against infinite loops
                    if row_iteration > 1:
                        return False

                    # Not on the last two tiles of the row
                    if target_value != goal_matrix[puzzle.row_in_progress][puzzle.right_col_progress - 1]:
                        move_tile(puzzle, target_value,
                                  goal_mapping[target_value]['row'],
                                  goal_mapping[target_value]['col'])
                        puzzle.row_progress_col += 1
                        target_value = goal_matrix[puzzle.row_in_progress][puzzle.row_progress_col]
                    else:
                        # We are on the last two values of the row - special handling
                        last_value = goal_matrix[puzzle.row_in_progress][puzzle.right_col_progress]

                        if puzzle.solving_row_top_down:
                            # Move last value two rows below its goal
                            move_tile(puzzle, last_value,
                                      goal_mapping[last_value]['row'] + 2,
                                      goal_mapping[last_value]['col'])
                            # Move 2nd to last value into last value's goal position
                            move_tile(puzzle, target_value,
                                      goal_mapping[last_value]['row'],
                                      goal_mapping[last_value]['col'])
                            # Move last value to below the 2nd to last value
                            move_tile(puzzle, last_value,
                                      goal_mapping[last_value]['row'] + 1,
                                      goal_mapping[last_value]['col'])

                            # Move to left of our 2nd to last value and slide into place
                            move_blank_to_col(puzzle, goal_mapping[last_value]['col'] - 1)
                            move_blank_to_row(puzzle, goal_mapping[last_value]['row'])
                            puzzle.slide_right()
                            puzzle.slide_down()
                        else:
                            # Solving row on the bottom - same logic but flipped
                            move_tile(puzzle, last_value,
                                      goal_mapping[last_value]['row'] - 2,
                                      goal_mapping[last_value]['col'])
                            move_tile(puzzle, target_value,
                                      goal_mapping[last_value]['row'],
                                      goal_mapping[last_value]['col'])
                            move_tile(puzzle, last_value,
                                      goal_mapping[last_value]['row'] - 1,
                                      goal_mapping[last_value]['col'])
                            move_blank_to_col(puzzle, goal_mapping[last_value]['col'] - 1)
                            move_blank_to_row(puzzle, goal_mapping[last_value]['row'])
                            puzzle.slide_right()
                            puzzle.slide_up()

                        # Reset the target in case we got into a bad state
                        row_iteration += 1
                        puzzle.row_progress_col = 0
                        target_value = goal_matrix[puzzle.row_in_progress][puzzle.row_progress_col]

        # While there are more unsolved columns than rows, solve columns
        while more_than_two_unsolved_cols(puzzle) and more_unsolved_cols_than_rows(puzzle):
            puzzle.solving_row = False

            if col_finished_and_not_in_goal_col(goal_puzzle, puzzle):
                puzzle.col_progress_row = 0

                if puzzle.solving_col_left_right:
                    puzzle.left_col_progress += 1
                    puzzle.col_in_progress = puzzle.left_col_progress
                else:
                    puzzle.right_col_progress -= 1
                    puzzle.col_in_progress = puzzle.right_col_progress
            else:
                if puzzle.solving_col_left_right:
                    # Once we've reached the goal state's blank col, start solving from the right
                    if puzzle.col_in_progress == goal_puzzle.blank_col:
                        puzzle.solving_col_left_right = False
                        puzzle.col_in_progress = puzzle.right_col_progress
                    else:
                        puzzle.col_in_progress = puzzle.left_col_progress
                else:
                    puzzle.col_in_progress = puzzle.right_col_progress

                col_iteration = 0
                target_value = goal_matrix[puzzle.top_row_progress][puzzle.col_in_progress]

                while not Puzzle.is_col_equal(goal_puzzle, puzzle, puzzle.col_in_progress):
                    # Guard against infinite loops
                    if col_iteration > 1:
                        return False

                    # Not on the last two tiles of the column
                    if target_value != goal_matrix[puzzle.bot_row_progress - 1][puzzle.col_in_progress]:
                        move_tile(puzzle, target_value,
                                  goal_mapping[target_value]['row'],
                                  goal_mapping[target_value]['col'])
                        puzzle.col_progress_row += 1
                        target_value = goal_matrix[puzzle.col_progress_row][puzzle.col_in_progress]
                    else:
                        # We are on the last two values of the column - special handling
                        last_value = goal_matrix[puzzle.bot_row_progress][puzzle.col_in_progress]

                        if puzzle.solving_col_left_right:
                            # Move last value two cols right of its goal
                            move_tile(puzzle, last_value,
                                      goal_mapping[last_value]['row'],
                                      goal_mapping[last_value]['col'] + 2)
                            # Move 2nd to last value into last value's goal position
                            move_tile(puzzle, target_value,
                                      goal_mapping[last_value]['row'],
                                      goal_mapping[last_value]['col'])
                            # Move last value to the right of the 2nd to last value
                            move_tile(puzzle, last_value,
                                      goal_mapping[last_value]['row'],
                                      goal_mapping[last_value]['col'] + 1)

                            # Move above our 2nd to last value and slide into place
                            move_blank_to_row(puzzle, goal_mapping[last_value]['row'] - 1)
                            move_blank_to_col(puzzle, goal_mapping[last_value]['col'])
                            puzzle.slide_down()
                            puzzle.slide_right()
                        else:
                            # Solving column on the right - same logic but flipped
                            move_tile(puzzle, last_value,
                                      goal_mapping[last_value]['row'],
                                      goal_mapping[last_value]['col'] - 2)
                            move_tile(puzzle, target_value,
                                      goal_mapping[last_value]['row'],
                                      goal_mapping[last_value]['col'])
                            move_tile(puzzle, last_value,
                                      goal_mapping[last_value]['row'],
                                      goal_mapping[last_value]['col'] - 1)
                            move_blank_to_row(puzzle, goal_mapping[last_value]['row'] - 1)
                            move_blank_to_col(puzzle, goal_mapping[last_value]['col'])
                            puzzle.slide_down()
                            puzzle.slide_left()

                        # Reset the target in case we got into a bad state
                        col_iteration += 1
                        puzzle.col_progress_row = 0
                        target_value = goal_matrix[puzzle.col_progress_row][puzzle.col_in_progress]

        # When down to a 2x2, rotate blank in circles until in goal state
        if unsolved_puzzle_is_two_by_two(puzzle):
            iterations = 0
            slide_vertically = True

            while not goal_puzzle.is_equal_to_puzzle(puzzle):
                if slide_vertically:
                    if puzzle.can_slide_down() and puzzle.blank_row - 1 <= goal_puzzle.blank_row - 1:
                        puzzle.slide_down()
                    else:
                        puzzle.slide_up()
                    slide_vertically = False
                else:
                    if puzzle.can_slide_right() and puzzle.blank_col + 1 <= goal_puzzle.blank_col + 1:
                        puzzle.slide_right()
                    else:
                        puzzle.slide_left()
                    slide_vertically = True

                iterations += 1
                if iterations > 20:
                    return False

    end_time = time.time()
    return {
        'solution_puzzle': puzzle,
        'runtime_ms': (end_time - start_time) * 1000,
        'coord_moves': puzzle.coord_moves,
        'max_puzzles_in_memory': 1,
    }


class StrategicSolver:
    """Strategic solver that wraps both BFS and Human-like approaches."""

    def __init__(self, size, max_time=120.0, solver_name=Solvers.HUMAN):
        self.size = size
        self.max_time = max_time
        self.solver = solver_name
        self.nodes_expanded = 0
        self.human_steps = 0
        self.moves = []

    def solve(self, initial_board, initial_empty_pos):
        """Solve puzzle and return list of moves or None if unsolvable."""
        if self.solver == Solvers.BFS:
            return self.solve_bfs(initial_board, initial_empty_pos)
        elif self.solver == Solvers.HUMAN:
            return self.solve_human(initial_board, initial_empty_pos)

    def solve_human(self, initial_board, initial_empty_pos):
        """Solve using human-like strategic approach."""
        # Create puzzle objects
        puzzle = Puzzle(initial_board)

        # Create goal state
        goal_board = self._create_goal_board()
        goal_puzzle = Puzzle(goal_board)

        # Solve
        result = solve_puzzle_strategically(puzzle, goal_puzzle)

        if result is False:
            return None

        # Return coordinate tuples (row, col) of tiles being moved
        self.moves = result['coord_moves']
        self.human_steps = len(self.moves)

        return self.moves

    def _create_goal_board(self):
        """Create the standard goal state for the puzzle."""
        goal = []
        value = 1
        for i in range(self.size):
            row = []
            for j in range(self.size):
                if i == self.size - 1 and j == self.size - 1:
                    row.append(0)
                else:
                    row.append(value)
                    value += 1
            goal.append(row)
        return goal

    #########################################################
    # BFS
    #########################################################
    def solve_bfs(self, initial_board, initial_empty_pos):
        """Solve puzzle using greedy best-first search."""
        start_time = time.time()
        self.nodes_expanded = 0

        h_cost = manhattan_distance(initial_board, self.size)
        initial_state = PuzzleState(initial_board, initial_empty_pos, 0, h_cost)

        open_set = []
        heapq.heappush(open_set, initial_state)

        closed_set = set()

        while open_set:
            if time.time() - start_time > self.max_time:
                return None

            current = heapq.heappop(open_set)

            if current in closed_set:
                continue

            self.nodes_expanded += 1

            if self._is_goal(current.board):
                return self._reconstruct_path(current)

            closed_set.add(current)

            neighbors = self._get_neighbors(current)

            for neighbor in neighbors:
                if neighbor not in closed_set:
                    heapq.heappush(open_set, neighbor)

        return None

    def _is_goal(self, board):
        expected = 1
        for i in range(self.size):
            for j in range(self.size):
                if i == self.size - 1 and j == self.size - 1:
                    return board[i][j] == 0
                if board[i][j] != expected:
                    return False
                expected += 1
        return True

    def _get_neighbors(self, state):
        neighbors = []
        row, col = state.empty_pos

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc

            if 0 <= new_row < self.size and 0 <= new_col < self.size:
                new_board = deepcopy(state.board)
                new_board[row][col] = new_board[new_row][new_col]
                new_board[new_row][new_col] = 0

                g_cost = state.g_cost + 1
                h_cost = manhattan_distance(new_board, self.size)

                neighbor = PuzzleState(
                    new_board,
                    (new_row, new_col),
                    g_cost,
                    h_cost,
                    state,
                    (new_row, new_col)
                )
                neighbors.append(neighbor)

        return neighbors

    def _reconstruct_path(self, goal_state):
        path = []
        current = goal_state

        while current.parent is not None:
            if current.move:
                path.append(current.move)
            current = current.parent

        path.reverse()
        return path
