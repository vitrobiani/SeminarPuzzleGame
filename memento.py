"""
Memento Pattern Module
======================
This module implements the Memento design pattern for undo/redo functionality.

The Memento pattern allows capturing and externalizing an object's internal state
so that the object can be restored to this state later.

Classes:
    PuzzleMemento: Stores a snapshot of puzzle state
    PuzzleCaretaker: Manages history of puzzle states
"""

from typing import List, Tuple, Optional
from copy import deepcopy


class PuzzleMemento:
    """
    Stores a snapshot of the puzzle state.
    
    This is an immutable representation of a puzzle configuration
    that can be used to restore the puzzle to a previous state.
    
    Attributes:
        board (List[List[int]]): Snapshot of the board state
        empty_pos (Tuple[int, int]): Position of empty tile
        move_count (int): Number of moves at this state
    """
    
    def __init__(self, board: List[List[int]], empty_pos: Tuple[int, int], move_count: int):
        """
        Create a memento with puzzle state.
        
        Args:
            board: 2D list representing board state
            empty_pos: Position of empty tile
            move_count: Number of moves made
        """
        self._board = deepcopy(board)
        self._empty_pos = empty_pos
        self._move_count = move_count
    
    def get_state(self) -> Tuple[List[List[int]], Tuple[int, int], int]:
        """
        Retrieve the stored state.
        
        Returns:
            Tuple containing (board, empty_pos, move_count)
        """
        return deepcopy(self._board), self._empty_pos, self._move_count


class PuzzleCaretaker:
    """
    Manages the history of puzzle states for undo/redo operations.
    
    Maintains two stacks: one for undo history and one for redo history.
    When a new move is made, it's added to undo history and redo is cleared.
    
    Attributes:
        undo_stack (List[PuzzleMemento]): Stack of previous states
        redo_stack (List[PuzzleMemento]): Stack of undone states
    """
    
    def __init__(self):
        """Initialize empty undo and redo stacks."""
        self.undo_stack: List[PuzzleMemento] = []
        self.redo_stack: List[PuzzleMemento] = []
    
    def save_state(self, board: List[List[int]], empty_pos: Tuple[int, int], move_count: int):
        """
        Save the current state to undo stack.
        
        Clears the redo stack when a new state is saved.
        
        Args:
            board: Current board state
            empty_pos: Current empty tile position
            move_count: Current move count
        """
        memento = PuzzleMemento(board, empty_pos, move_count)
        self.undo_stack.append(memento)
        # Clear redo stack when new move is made
        self.redo_stack.clear()
    
    def undo(self) -> Optional[Tuple[List[List[int]], Tuple[int, int], int]]:
        """
        Undo the last move.
        
        Moves the current state to redo stack and retrieves previous state.
        
        Returns:
            Optional[Tuple]: Previous state if available, None otherwise
        """
        if not self.can_undo():
            return None
        
        # Move current state to redo stack
        current_memento = self.undo_stack.pop()
        self.redo_stack.append(current_memento)
        
        # Get previous state
        if self.undo_stack:
            return self.undo_stack[-1].get_state()
        
        return None
    
    def redo(self) -> Optional[Tuple[List[List[int]], Tuple[int, int], int]]:
        """
        Redo a previously undone move.
        
        Moves state from redo stack back to undo stack.
        
        Returns:
            Optional[Tuple]: Next state if available, None otherwise
        """
        if not self.can_redo():
            return None
        
        # Move from redo to undo
        memento = self.redo_stack.pop()
        self.undo_stack.append(memento)
        
        return memento.get_state()
    
    def can_undo(self) -> bool:
        """
        Check if undo operation is available.
        
        Returns:
            bool: True if there are states to undo
        """
        return len(self.undo_stack) > 1  # Keep at least initial state
    
    def can_redo(self) -> bool:
        """
        Check if redo operation is available.
        
        Returns:
            bool: True if there are states to redo
        """
        return len(self.redo_stack) > 0
    
    def clear(self):
        """Clear all history."""
        self.undo_stack.clear()
        self.redo_stack.clear()
    
    def get_undo_count(self) -> int:
        """
        Get number of available undo operations.
        
        Returns:
            int: Number of states in undo stack (minus current)
        """
        return max(0, len(self.undo_stack) - 1)
    
    def get_redo_count(self) -> int:
        """
        Get number of available redo operations.
        
        Returns:
            int: Number of states in redo stack
        """
        return len(self.redo_stack)
