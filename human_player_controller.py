"""
Human Player Controller Module
==============================
This module implements the Controller for human player in MVC pattern.

Classes:
    HumanPlayerController: Manages interaction between Model and View
"""

from puzzle_model import PuzzleModel
from human_player_view import HumanPlayerView
from memento import PuzzleCaretaker
from statistics import StatsTracker
from typing import Optional
import socket
import threading
import pickle


class HumanPlayerController:
    """
    Controller for human player puzzle game.
    
    Implements the Controller component of MVC pattern.
    Manages game logic and coordinates between Model and View.
    
    Attributes:
        client_id (int): Client identifier
        model (PuzzleModel): Puzzle model
        view (HumanPlayerView): GUI view
        caretaker (PuzzleCaretaker): Memento manager for undo/redo
        stats_tracker (StatsTracker): Statistics tracker
        socket (socket.socket): Network socket for communication
        current_game_solvable (bool): Whether current game is solvable
    """
    
    def __init__(self, client_id: int, host: str = 'localhost', port: int = 5000):
        """
        Initialize the human player controller.
        
        Args:
            client_id: Client identifier
            host: Server host
            port: Server port
        """
        self.client_id = client_id

        # Check if view already exists (Singleton)
        self.view = HumanPlayerView(client_id=client_id, initial_size=3)

        # If view already existed, don't reinitialize
        if hasattr(self.view, 'controller_initialized') and self.view.controller_initialized:
            return

        self.view.controller_initialized = True

        self.model = PuzzleModel(size=3)
        self.caretaker = PuzzleCaretaker()
        self.stats_tracker = StatsTracker(client_id)

        # Network
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None

        # Game state
        self.current_game_solvable = True
        self.game_finished = False

        # Load existing statistics
        self.stats_tracker.load_from_file(f"stats_client_{client_id}.json")

        # Set up view callbacks
        self._setup_callbacks()

        # Connect to server
        self._connect_to_server()

        # Start new game
        self.new_game()

    def _setup_callbacks(self):
        """Set up view callbacks."""
        self.view.on_tile_click = self.handle_tile_click
        self.view.on_new_game = self.new_game
        self.view.on_size_change = self.handle_size_change
        self.view.on_undo = self.handle_undo
        self.view.on_redo = self.handle_redo
        self.view.on_close = self.handle_close

    def _connect_to_server(self):
        """Connect to the server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))

            # Send client info
            client_info = {
                'type': 'human',
                'client_id': self.client_id
            }
            self.socket.send(pickle.dumps(client_info))

            self._log_to_server(f"Client {self.client_id} connected (Human Player)")

        except Exception as e:
            print(f"Could not connect to server: {e}")
            self.socket = None

    def _log_to_server(self, message: str):
        """
        Send log message to server.

        Args:
            message: Log message
        """
        if self.socket:
            try:
                log_data = {
                    'action': 'log',
                    'message': message
                }
                self.socket.send(pickle.dumps(log_data))
            except:
                pass

    def new_game(self):
        """Start a new game."""
        # Record abandoned game if applicable
        if not self.game_finished and self.caretaker.get_undo_count() > 0:
            if self.current_game_solvable:
                self.stats_tracker.record_abandoned(self.model.size)
                self._log_to_server(f"Client {self.client_id}: Game abandoned ({self.model.size}x{self.model.size})")

        # Generate new puzzle
        self.model.generate_random_board()

        # Check solvability
        self.current_game_solvable = self.model.is_solvable()

        if not self.current_game_solvable:
            self.view.update_status("This puzzle is UNSOLVABLE! Click 'New Game' to try another puzzle.", "red")
            self.stats_tracker.record_unsolvable(self.model.size)
            self._log_to_server(f"Client {self.client_id}: Unsolvable puzzle generated ({self.model.size}x{self.model.size})")
        else:
            self.view.update_status("Game started! Move tiles to solve the puzzle.", "blue")
            self._log_to_server(f"Client {self.client_id}: New game started ({self.model.size}x{self.model.size})")

        # Reset state
        self.caretaker.clear()
        self.caretaker.save_state(
            self.model.get_board_copy(),
            self.model.empty_pos,
            self.model.move_count
        )
        self.game_finished = False

        # Update view
        self.view.update_board(self.model.board)
        self.view.update_move_count(0)
        self.view.update_undo_redo_buttons(False, False)
        self.view.start_timer()

    def handle_tile_click(self, row: int, col: int):
        """
        Handle tile click event.

        Args:
            row: Row of clicked tile
            col: Column of clicked tile
        """
        if self.game_finished:
            return

        if not self.current_game_solvable:
            return

        # Try to move tile
        if self.model.move((row, col)):
            # Save state for undo
            self.caretaker.save_state(
                self.model.get_board_copy(),
                self.model.empty_pos,
                self.model.move_count
            )

            # Update view
            self.view.update_board(self.model.board)
            self.view.update_move_count(self.model.move_count)
            self.view.update_undo_redo_buttons(
                self.caretaker.can_undo(),
                self.caretaker.can_redo()
            )

            # Check if solved
            if self.model.is_solved():
                self.handle_game_won()

    def handle_game_won(self):
        """Handle game completion."""
        self.game_finished = True
        self.view.stop_timer()
        elapsed_time = self.view.get_elapsed_time()

        self.view.update_status(
            f"🎉 Congratulations! Puzzle Solved in {self.model.move_count} moves and {elapsed_time:.1f} seconds! 🎉",
            "green"
        )

        # Record statistics
        self.stats_tracker.record_solved(
            self.model.size,
            elapsed_time,
            self.model.move_count
        )
        self.stats_tracker.save_to_file(f"stats_client_{self.client_id}.json")

        # Log to server
        self._log_to_server(
            f"Client {self.client_id}: Puzzle solved! " +
            f"Size: {self.model.size}x{self.model.size}, " +
            f"Moves: {self.model.move_count}, " +
            f"Time: {elapsed_time:.1f}s"
        )

    def handle_size_change(self, new_size: int):
        """
        Handle board size change.

        Args:
            new_size: New puzzle dimension
        """
        if new_size != self.model.size:
            # Record abandoned game if applicable
            if not self.game_finished and self.caretaker.get_undo_count() > 0:
                if self.current_game_solvable:
                    self.stats_tracker.record_abandoned(self.model.size)
                    self._log_to_server(f"Client {self.client_id}: Game abandoned due to size change")

            self.model.resize(new_size)
            self.view.resize_board(new_size)
            self._log_to_server(f"Client {self.client_id}: Board size changed to {new_size}x{new_size}")
            self.new_game()

    def handle_undo(self):
        """Handle undo action."""
        if not self.current_game_solvable:
            return

        state = self.caretaker.undo()
        if state:
            board, empty_pos, move_count = state
            self.model.set_board(board, empty_pos, move_count)

            self.view.update_board(self.model.board)
            self.view.update_move_count(self.model.move_count)
            self.view.update_undo_redo_buttons(
                self.caretaker.can_undo(),
                self.caretaker.can_redo()
            )

    def handle_redo(self):
        """Handle redo action."""
        if not self.current_game_solvable:
            return

        state = self.caretaker.redo()
        if state:
            board, empty_pos, move_count = state
            self.model.set_board(board, empty_pos, move_count)

            self.view.update_board(self.model.board)
            self.view.update_move_count(self.model.move_count)
            self.view.update_undo_redo_buttons(
                self.caretaker.can_undo(),
                self.caretaker.can_redo()
            )

            # Check if solved after redo
            if self.model.is_solved() and not self.game_finished:
                self.handle_game_won()

    def handle_close(self):
        """Handle window close."""
        # Record abandoned game if applicable
        if not self.game_finished and self.caretaker.get_undo_count() > 0:
            if self.current_game_solvable:
                self.stats_tracker.record_abandoned(self.model.size)

        # Save statistics
        self.stats_tracker.save_to_file(f"stats_client_{self.client_id}.json")

        # Disconnect from server
        if self.socket:
            self._log_to_server(f"Client {self.client_id} disconnecting")
            try:
                self.socket.close()
            except:
                pass

    def run(self):
        """Run the controller."""
        self.view.run()