"""
A* Solver Module
================
This module implements the A* algorithm for solving sliding puzzles.

The A* algorithm uses a heuristic function (Manhattan distance) to find
an optimal or near-optimal solution path.

Classes:
    PuzzleState: Represents a state in the search space
    AStarSolver: Implements A* algorithm for puzzle solving
    
Functions:
    manhattan_distance: Heuristic function for A*
"""

import heapq
import time
from typing import List, Tuple, Optional
from copy import deepcopy


class PuzzleState:
    """
    Represents a state in the puzzle search space.
    
    Used by A* algorithm to track puzzle configurations during search.
    
    Attributes:
        board (List[List[int]]): Current board configuration
        empty_pos (Tuple[int, int]): Position of empty tile
        g_cost (int): Cost from start to this state (moves made)
        h_cost (int): Heuristic cost to goal (Manhattan distance)
        f_cost (int): Total cost (g_cost + h_cost)
        parent (Optional[PuzzleState]): Previous state in path
        move (Optional[Tuple[int, int]]): Move that led to this state
    """
    
    def __init__(self, board: List[List[int]], empty_pos: Tuple[int, int], 
                 g_cost: int, h_cost: int, parent=None, move=None):
        """
        Initialize a puzzle state.
        
        Args:
            board: Current board configuration
            empty_pos: Position of empty tile
            g_cost: Cost from start
            h_cost: Heuristic cost to goal
            parent: Previous state
            move: Move that created this state
        """
        self.board = board
        self.empty_pos = empty_pos
        self.g_cost = g_cost
        self.h_cost = h_cost
        self.f_cost = g_cost + h_cost
        self.parent = parent
        self.move = move
    
    def __lt__(self, other):
        """Compare states by f_cost for priority queue."""
        return self.f_cost < other.f_cost
    
    def __eq__(self, other):
        """Check if two states have the same board configuration."""
        return self.board == other.board
    
    def __hash__(self):
        """Hash based on board configuration for use in sets/dicts."""
        return hash(tuple(tuple(row) for row in self.board))


def manhattan_distance(board: List[List[int]], size: int) -> int:
    """
    Calculate Manhattan distance heuristic.
    
    The Manhattan distance is the sum of horizontal and vertical distances
    of each tile from its goal position.
    
    Args:
        board: Current board state
        size: Dimension of the board
        
    Returns:
        int: Manhattan distance to goal state
    """
    distance = 0
    for i in range(size):
        for j in range(size):
            value = board[i][j]
            if value != 0:
                # Calculate goal position for this value
                goal_row = (value - 1) // size
                goal_col = (value - 1) % size
                # Add Manhattan distance
                distance += abs(i - goal_row) + abs(j - goal_col)
    return distance


class AStarSolver:
    """
    Solves sliding puzzles using A* algorithm.
    
    The solver finds an optimal path from the initial state to the goal state
    using Manhattan distance as a heuristic.
    
    Attributes:
        size (int): Dimension of the puzzle
        max_time (float): Maximum time allowed for solving (seconds)
        nodes_expanded (int): Number of states explored
    """
    
    def __init__(self, size: int, max_time: float = 120.0):
        """
        Initialize A* solver.
        
        Args:
            size: Dimension of the puzzle
            max_time: Maximum solving time in seconds
        """
        self.size = size
        self.max_time = max_time
        self.nodes_expanded = 0
    
    def solve(self, initial_board: List[List[int]], initial_empty_pos: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        Solve the puzzle using A* algorithm.
        
        Args:
            initial_board: Starting board configuration
            initial_empty_pos: Starting position of empty tile
            
        Returns:
            Optional[List[Tuple[int, int]]]: List of moves (tile positions) to solve,
                                             or None if no solution found in time
        """
        start_time = time.time()
        self.nodes_expanded = 0
        
        # Create initial state
        h_cost = manhattan_distance(initial_board, self.size)
        initial_state = PuzzleState(initial_board, initial_empty_pos, 0, h_cost)
        
        # Priority queue (min-heap) for open set
        open_set = []
        heapq.heappush(open_set, initial_state)
        
        # Set of explored states
        closed_set = set()
        
        # Dictionary to track best g_cost for each state
        best_g = {initial_state: 0}
        
        while open_set:
            # Check timeout
            if time.time() - start_time > self.max_time:
                return None
            
            # Get state with lowest f_cost
            current = heapq.heappop(open_set)
            
            # Skip if we've already processed this state with better cost
            if current in closed_set:
                continue
            
            self.nodes_expanded += 1
            
            # Check if goal reached
            if self._is_goal(current.board):
                return self._reconstruct_path(current)
            
            closed_set.add(current)
            
            # Explore neighbors
            neighbors = self._get_neighbors(current)
            
            for neighbor in neighbors:
                if neighbor in closed_set:
                    continue
                
                # Check if this path to neighbor is better
                if neighbor not in best_g or neighbor.g_cost < best_g[neighbor]:
                    best_g[neighbor] = neighbor.g_cost
                    heapq.heappush(open_set, neighbor)
        
        # No solution found
        return None
    
    def _is_goal(self, board: List[List[int]]) -> bool:
        """
        Check if board is in goal state.
        
        Args:
            board: Board to check
            
        Returns:
            bool: True if in goal state
        """
        expected = 1
        for i in range(self.size):
            for j in range(self.size):
                if i == self.size - 1 and j == self.size - 1:
                    return board[i][j] == 0
                if board[i][j] != expected:
                    return False
                expected += 1
        return True
    
    def _get_neighbors(self, state: PuzzleState) -> List[PuzzleState]:
        """
        Get all neighboring states from current state.
        
        Args:
            state: Current state
            
        Returns:
            List[PuzzleState]: List of neighbor states
        """
        neighbors = []
        row, col = state.empty_pos
        
        # Possible moves: up, down, left, right
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            
            if 0 <= new_row < self.size and 0 <= new_col < self.size:
                # Create new board state
                new_board = deepcopy(state.board)
                new_board[row][col] = new_board[new_row][new_col]
                new_board[new_row][new_col] = 0
                
                # Calculate costs
                g_cost = state.g_cost + 1
                h_cost = manhattan_distance(new_board, self.size)
                
                # Create neighbor state
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
    
    def _reconstruct_path(self, goal_state: PuzzleState) -> List[Tuple[int, int]]:
        """
        Reconstruct the path from initial state to goal.
        
        Args:
            goal_state: The goal state reached
            
        Returns:
            List[Tuple[int, int]]: List of moves (tile positions) to reach goal
        """
        path = []
        current = goal_state
        
        while current.parent is not None:
            if current.move:
                path.append(current.move)
            current = current.parent
        
        path.reverse()
        return path
    
    def get_nodes_expanded(self) -> int:
        """
        Get number of nodes expanded during last solve.
        
        Returns:
            int: Number of states explored
        """
        return self.nodes_expanded
