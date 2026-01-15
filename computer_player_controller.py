"""
Computer Player Controller Module
=================================
This module implements the Controller for computer player in MVC pattern.

Classes:
    ComputerPlayerController: Manages AI solving of puzzles
"""

from puzzle_model import PuzzleModel
from computer_player_view import ComputerPlayerView
from strategic_solver import StrategicSolver  # Changed from astar_solver
from statistics import StatsTracker
from typing import Optional, List, Tuple
import socket
import threading
import pickle
import time


class ComputerPlayerController:
    """
    Controller for computer player puzzle solver.

    Implements the Controller component of MVC pattern for AI solver.
    Uses A* algorithm to automatically solve puzzles.

    Attributes:
        model (PuzzleModel): Puzzle model
        view (ComputerPlayerView): GUI view
        solver (AStarSolver): A* solver
        socket (socket.socket): Network socket for communication
        solving_thread (threading.Thread): Thread for solving
    """

    def __init__(self, host: str = 'localhost', port: int = 5000):
        """
        Initialize the computer player controller.

        Args:
            host: Server host
            port: Server port
        """
        self.model = PuzzleModel(size=3)
        self.view = ComputerPlayerView(initial_size=3)
        self.max_time = 120.0  # seconds
        self.solver = StrategicSolver(size=3, max_time=self.max_time)  # Changed from AStarSolver

        # Statistics
        self.stats_tracker = StatsTracker(client_id='computer')
        self.stats_tracker.load_from_file("stats_computer.json")

        # Network
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None

        # Threading
        self.solving_thread: Optional[threading.Thread] = None
        self.stop_solving = False

        # Timing
        self.solve_start_time = 0.0

        # Set up view callbacks
        self._setup_callbacks()

        # Connect to server
        self._connect_to_server()

        # Initialize view
        self.view.update_board(self.model.board)

    def _setup_callbacks(self):
        """Set up view callbacks."""
        self.view.on_new_game = self.new_game
        self.view.on_solve_game = self.solve_game
        self.view.on_new_game_and_solve = self.new_game_and_solve
        self.view.on_size_change = self.handle_size_change
        self.view.on_close = self.handle_close

    def _connect_to_server(self):
        """Connect to the server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))

            # Send client info
            client_info = {
                'type': 'computer',
                'client_id': 'computer'
            }
            self.socket.send(pickle.dumps(client_info))

            self._log_to_server("Computer Player connected")

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
        """
        Generate a new puzzle without solving.

        Creates a fresh random puzzle board and updates the display.
        """

        if self.solving_thread and self.solving_thread.is_alive():
            return

        # Generate new puzzle
        self.model.generate_random_board()
        self.view.update_board(self.model.board)
        self.view.update_move_count(0)
        self.view.update_status("New game started. Click 'Solve Game' to solve it.", "blue")
        self.view.update_progress("")

        # Check solvability
        if not self.model.is_solvable():
            self.view.update_status("This puzzle is UNSOLVABLE!", "red")
            self._log_to_server(f"Computer: Unsolvable puzzle ({self.model.size}x{self.model.size})")
            return

        self._log_to_server(f"Computer: New game started ({self.model.size}x{self.model.size})")

    def solve_game(self):
        """
        Solve the current puzzle without generating a new one.

        Checks solvability and uses the strategic solver algorithm.
        """
        if self.solving_thread and self.solving_thread.is_alive():
            return

        # Check solvability
        if not self.model.is_solvable():
            self.view.update_status("This puzzle is UNSOLVABLE!", "red")
            self._log_to_server(f"Computer: Unsolvable puzzle ({self.model.size}x{self.model.size})")
            return

        self._log_to_server(f"Computer: Starting to solve {self.model.size}x{self.model.size} puzzle")

        # Start solving in separate thread
        self.stop_solving = False
        self.solving_thread = threading.Thread(target=self._solve_puzzle_thread)
        self.solving_thread.daemon = True
        self.solving_thread.start()

    def new_game_and_solve(self):
        """
        Generate a new puzzle and solve it automatically.

        Combines new_game() and solve_game() functionality.
        Retries if an unsolvable puzzle is generated.
        """
        if self.solving_thread and self.solving_thread.is_alive():
            return

        # Generate new puzzle
        self.model.generate_random_board()
        self.view.update_board(self.model.board)
        self.view.update_move_count(0)
        self.view.update_progress("")

        # Check solvability
        if not self.model.is_solvable():
            self.view.update_status("This puzzle is UNSOLVABLE! Generating a new one...", "red")
            self._log_to_server(f"Computer: Unsolvable puzzle generated ({self.model.size}x{self.model.size})")
            # Try again after 1 second
            self.view.root.after(1000, self.new_game_and_solve)
            return

        # Now solve it
        self._log_to_server(f"Computer: Starting to solve {self.model.size}x{self.model.size} puzzle")

        # Start solving in separate thread
        self.stop_solving = False
        self.solving_thread = threading.Thread(target=self._solve_puzzle_thread)
        self.solving_thread.daemon = True
        self.solving_thread.start()

    def _solve_puzzle_thread(self):
        """Solve puzzle in separate thread."""
        self.view.set_solving(True)
        self.view.update_status("Solving puzzle using A* algorithm...", "orange")
        self.view.update_progress("Computing solution...")

        self.solve_start_time = time.time()

        # Solve using A*
        solution = self.solver.solve(
            self.model.get_board_copy(),
            self.model.empty_pos
        )

        solve_time = time.time() - self.solve_start_time

        if solution is None:
            # Timeout or no solution
            self.view.update_status(f"Could not solve puzzle in time limit ({self.max_time}). The puzzle may be too complex.", "red")
            self.view.update_progress("")
            self._log_to_server(
                f"Computer: Failed to solve {self.model.size}x{self.model.size} puzzle (timeout)"
            )
            self.view.set_solving(False)
            return

        self.view.update_progress(f"Solution found! {len(solution)} moves. Executing...")
        self._log_to_server(
            f"Computer: Solution found in {solve_time:.5f}s - {len(solution)} moves " +
            f"(Strategic Algorithm)"
        )

        # Execute solution moves with animation
        self._execute_solution(solution)

        self.view.set_solving(False)

    def _execute_solution(self, solution: List[Tuple[int, int]]):
        """
        Execute solution moves with animation.

        Args:
            solution: List of moves to execute
        """
        for i, move in enumerate(solution):
            if self.stop_solving:
                break

            # Execute move
            self.model.move(move)

            # Update view
            self.view.root.after(0, self.view.update_board, self.model.get_board_copy())
            self.view.root.after(0, self.view.update_move_count, self.model.move_count)
            self.view.root.after(0, self.view.update_progress,
                               f"Executing move {i+1}/{len(solution)}")

            # Get speed from slider and calculate delay
            speed_multiplier = self.view.get_animation_speed()
            move_delay = 200 / speed_multiplier  # Base 200ms at 1.0x

            time.sleep(move_delay / 1000.0)

        # Check if solved
        if self.model.is_solved():
            self.view.root.after(0, self._handle_puzzle_solved, len(solution))
        else:
            self.view.root.after(0, self.view.update_status,
                               "Solution execution interrupted", "red")

    def _handle_puzzle_solved(self, num_moves: int):
        """
        Handle puzzle completion.

        Args:
            num_moves: Number of moves to solve
        """
        # Calculate total time (from start of solving to completion)
        total_time = time.time() - self.solve_start_time

        self.view.update_status(
            f"✓ Puzzle Solved Successfully! {num_moves} moves in {total_time:.2f}s (Strategic Algorithm)",
            "green"
        )
        self.view.update_progress("")

        # Record statistics
        self.stats_tracker.record_solved(
            self.model.size,
            total_time,
            num_moves
        )
        self.stats_tracker.save_to_file("stats_computer.json")

        self._log_to_server(
            f"Computer: Puzzle solved! " +
            f"Size: {self.model.size}x{self.model.size}, " +
            f"Moves: {num_moves}, " +
            f"Time: {total_time:.2f}s"
        )

    def handle_size_change(self, new_size: int):
        """
        Handle board size change.

        Args:
            new_size: New puzzle dimension
        """
        if new_size != self.model.size:
            # Stop any ongoing solving
            self.stop_solving = True
            if self.solving_thread:
                self.solving_thread.join(timeout=1.0)

            # Update model and solver
            self.model.resize(new_size)
            self.solver = StrategicSolver(size=new_size, max_time=120.0)  # Changed from AStarSolver

            # Update view
            self.view.resize_board(new_size)
            self.view.update_board(self.model.board)
            self.view.update_move_count(0)
            self.view.update_status(f"Board size changed to {new_size}x{new_size}. Ready to start!", "blue")
            self.view.update_progress("")

            self._log_to_server(f"Computer: Board size changed to {new_size}x{new_size}")

    def handle_close(self):
        """Handle window close."""
        # Stop solving
        self.stop_solving = True
        if self.solving_thread:
            self.solving_thread.join(timeout=1.0)

        # Save statistics
        self.stats_tracker.save_to_file("stats_computer.json")

        # Disconnect from server
        if self.socket:
            self._log_to_server("Computer Player disconnecting")
            try:
                self.socket.close()
            except:
                pass

    def run(self):
        """Run the controller."""
        self.view.run()