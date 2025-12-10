"""
Puzzle Model Module
===================
This module contains the core logic for the sliding puzzle game.
It implements the Model part of the MVC pattern.

Classes:
    PuzzleModel: Represents the puzzle board state and operations
    
Functions:
    count_inversions: Counts inversions to check solvability
    is_solvable: Determines if a puzzle configuration is solvable
"""

import random
from typing import List, Tuple, Optional


class PuzzleModel:
    """
    Represents a sliding puzzle board.
    
    The puzzle consists of numbered tiles and one empty space.
    Tiles can be moved into the empty space.
    
    Attributes:
        size (int): Dimension of the square board (e.g., 3 for 3x3)
        board (List[List[int]]): 2D list representing the puzzle state
        empty_pos (Tuple[int, int]): Position of the empty tile (row, col)
        move_count (int): Number of moves made
    """
    
    def __init__(self, size: int = 3):
        """
        Initialize a puzzle model.
        
        Args:
            size: Dimension of the puzzle (3, 4, 5, or 6)
        """
        self.size = size
        self.board = []
        self.empty_pos = (0, 0)
        self.move_count = 0
        self.generate_random_board()
    
    def generate_random_board(self):
        """
        Generate a random puzzle board.
        
        Creates a shuffled board by randomly arranging numbers.
        The board may or may not be solvable.
        """
        numbers = list(range(self.size * self.size))
        random.shuffle(numbers)
        
        self.board = []
        for i in range(self.size):
            row = []
            for j in range(self.size):
                num = numbers[i * self.size + j]
                row.append(num)
                if num == 0:
                    self.empty_pos = (i, j)
            self.board.append(row)
        
        self.move_count = 0
    
    def is_solvable(self) -> bool:
        """
        Check if the current puzzle configuration is solvable.
        
        Uses inversion counting algorithm:
        - For odd-sized boards: solvable if inversions are even
        - For even-sized boards: solvable if (inversions + empty_row from bottom) is odd
        
        Returns:
            bool: True if solvable, False otherwise
        """
        inversions = self._count_inversions()
        
        if self.size % 2 == 1:
            # Odd-sized board
            return inversions % 2 == 0
        else:
            # Even-sized board
            empty_row_from_bottom = self.size - self.empty_pos[0]
            return (inversions + empty_row_from_bottom) % 2 == 1
    
    def _count_inversions(self) -> int:
        """
        Count the number of inversions in the puzzle.
        
        An inversion is when a larger number appears before a smaller number
        when reading the board left-to-right, top-to-bottom (excluding 0).
        
        Returns:
            int: Number of inversions
        """
        flat_board = []
        for row in self.board:
            for num in row:
                if num != 0:
                    flat_board.append(num)
        
        inversions = 0
        for i in range(len(flat_board)):
            for j in range(i + 1, len(flat_board)):
                if flat_board[i] > flat_board[j]:
                    inversions += 1
        
        return inversions
    
    def is_solved(self) -> bool:
        """
        Check if the puzzle is in the solved state.
        
        Solved state has numbers in ascending order with 0 at the end.
        
        Returns:
            bool: True if solved, False otherwise
        """
        expected = 1
        for i in range(self.size):
            for j in range(self.size):
                if i == self.size - 1 and j == self.size - 1:
                    # Last position should be 0
                    return self.board[i][j] == 0
                if self.board[i][j] != expected:
                    return False
                expected += 1
        return True
    
    def get_possible_moves(self) -> List[Tuple[int, int]]:
        """
        Get all valid moves from current position.
        
        Returns positions of tiles that can be moved into the empty space.
        
        Returns:
            List[Tuple[int, int]]: List of (row, col) positions that can move
        """
        row, col = self.empty_pos
        moves = []
        
        # Check all four directions
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < self.size and 0 <= new_col < self.size:
                moves.append((new_row, new_col))
        
        return moves
    
    def move(self, tile_pos: Tuple[int, int]) -> bool:
        """
        Move a tile into the empty space.
        
        Args:
            tile_pos: Position (row, col) of the tile to move
            
        Returns:
            bool: True if move was valid and executed, False otherwise
        """
        if tile_pos not in self.get_possible_moves():
            return False
        
        # Swap tile with empty space
        tile_row, tile_col = tile_pos
        empty_row, empty_col = self.empty_pos
        
        self.board[empty_row][empty_col] = self.board[tile_row][tile_col]
        self.board[tile_row][tile_col] = 0
        
        self.empty_pos = (tile_row, tile_col)
        self.move_count += 1
        
        return True
    
    def get_board_copy(self) -> List[List[int]]:
        """
        Get a deep copy of the current board state.
        
        Returns:
            List[List[int]]: Copy of the board
        """
        return [row[:] for row in self.board]
    
    def set_board(self, board: List[List[int]], empty_pos: Tuple[int, int], move_count: int = 0):
        """
        Set the board to a specific state.
        
        Used for restoring states in Memento pattern.
        
        Args:
            board: 2D list representing board state
            empty_pos: Position of empty tile
            move_count: Number of moves in this state
        """
        self.board = [row[:] for row in board]
        self.empty_pos = empty_pos
        self.move_count = move_count
    
    def get_tile_at(self, row: int, col: int) -> int:
        """
        Get the value of the tile at a specific position.
        
        Args:
            row: Row index
            col: Column index
            
        Returns:
            int: Tile value (0 for empty)
        """
        return self.board[row][col]
    
    def resize(self, new_size: int):
        """
        Change the puzzle size and generate a new board.
        
        Args:
            new_size: New dimension (3, 4, 5, or 6)
        """
        self.size = new_size
        self.generate_random_board()
    
    def __str__(self) -> str:
        """
        String representation of the puzzle.
        
        Returns:
            str: Formatted board display
        """
        result = []
        for row in self.board:
            row_str = " ".join(f"{num:2}" if num != 0 else "  " for num in row)
            result.append(row_str)
        return "\n".join(result)
