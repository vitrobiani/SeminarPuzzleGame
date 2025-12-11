"""
Greedy Best-First Search Solver
================================
This is a MODIFIED version of A* that only uses the heuristic (h).

Instead of f = g + h (A*), we use f = h (Greedy).
This makes it MUCH faster but solutions are not optimal.

Trade-off:
- A*: Optimal solution (50 moves) but timeouts
- Greedy: Non-optimal (150 moves) but completes in seconds
"""

import heapq
import time
from enum import Enum
from typing import List, Tuple, Optional
from copy import deepcopy


class PuzzleState:
    """State in puzzle search space."""

    def __init__(self, board, empty_pos, g_cost, h_cost, parent=None, move=None):
        self.board = board
        self.empty_pos = empty_pos
        self.g_cost = g_cost
        self.h_cost = h_cost
        # KEY CHANGE: Use only heuristic for greedy search!
        self.f_cost = h_cost  # NOT g_cost + h_cost
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
    AStar = "AStar"


class StrategicSolver:
    """Greedy Best-First Search solver (fast but non-optimal)."""

    def __init__(self, size, max_time=120.0, solver_name=Solvers.BFS):
        self.size = size
        self.max_time = max_time
        self.nodes_expanded = 0
        self.solver = solver_name

    def solve(self, initial_board, initial_empty_pos):
        """Solve puzzle and return list of moves or None if unsolvable."""
        return self.solve_bfs(initial_board, initial_empty_pos)

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
