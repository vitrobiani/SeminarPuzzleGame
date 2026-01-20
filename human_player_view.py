"""
Human Player GUI Module
=======================
This module implements the GUI (View) for the human player client.

It implements the View part of the MVC pattern using tkinter.

Classes:
    HumanPlayerView: GUI for human player interaction
"""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Optional, Dict
import time
import threading


class HumanPlayerView:
    """
    GUI View for human player puzzle game (Singleton - only one instance total).

    Implements the View component of MVC pattern.
    Displays the puzzle board and provides controls for gameplay.
    Only one human player window can exist at a time.

    Attributes:
        root (tk.Tk): Main window
        client_id (int): Client identifier
        size (int): Current puzzle dimension
        on_tile_click (Callable): Callback for tile clicks
        on_new_game (Callable): Callback for new game
        on_size_change (Callable): Callback for size change
        on_undo (Callable): Callback for undo
        on_redo (Callable): Callback for redo
        tile_buttons (Dict): Dictionary of tile buttons
    """

    _instance = None  # Single instance for Singleton
    _lock = threading.Lock()

    def __new__(cls, client_id: int, initial_size: int = 3):
        """Singleton pattern - only one instance total."""
        with cls._lock:
            if cls._instance is not None:
                # Instance already exists
                if cls._instance.root.winfo_exists():
                    # Bring existing window to front
                    cls._instance.root.lift()
                    cls._instance.root.focus_force()
                    return cls._instance
                else:
                    # Old instance destroyed, remove it
                    cls._instance = None

            # Create new instance
            instance = super().__new__(cls)
            cls._instance = instance
            return instance

    def __init__(self, client_id: int, initial_size: int = 3):
        """
        Initialize the human player view.

        Args:
            client_id: Client identifier
            initial_size: Initial puzzle dimension
        """
        # Check if already initialized (Singleton)
        if hasattr(self, '_initialized') and self._initialized:
            return

        self._initialized = True
        self.client_id = client_id
        self.size = initial_size
        self.root = tk.Tk()
        self.root.title(f"Sliding Puzzle - Client {client_id}")
        self.root.geometry("700x800")

        # Callbacks (set by controller)
        self.on_tile_click: Optional[Callable] = None
        self.on_new_game: Optional[Callable] = None
        self.on_size_change: Optional[Callable] = None
        self.on_undo: Optional[Callable] = None
        self.on_redo: Optional[Callable] = None
        self.on_close: Optional[Callable] = None

        # UI elements
        self.tile_buttons: Dict = {}
        self.move_label: Optional[tk.Label] = None
        self.time_label: Optional[tk.Label] = None
        self.status_label: Optional[tk.Label] = None

        # Timing
        self.start_time = time.time()
        self.timer_running = False

        self._create_ui()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)

    def _create_ui(self):
        """Create all UI elements."""
        # Top frame for controls
        control_frame = tk.Frame(self.root, pady=10)
        control_frame.pack()

        # Client ID label
        tk.Label(control_frame, text=f"Client {self.client_id}",
                font=("Arial", 14, "bold")).pack()

        # Size selection
        size_frame = tk.Frame(control_frame)
        size_frame.pack(pady=5)

        tk.Label(size_frame, text="Board Size:").pack(side=tk.LEFT, padx=5)

        self.size_var = tk.IntVar(value=self.size)
        for size in [3, 4, 5, 6, 7, 8, 9, 10]:
            tk.Radiobutton(size_frame, text=f"{size}x{size}",
                          variable=self.size_var, value=size,
                          command=self._handle_size_change).pack(side=tk.LEFT)

        # Button frame
        button_frame = tk.Frame(control_frame)
        button_frame.pack(pady=5)

        self.new_game_btn = tk.Button(button_frame, text="New Game",
                                      command=self._handle_new_game,
                                      font=("Arial", 12), bg="#4CAF50",
                                      fg="white", padx=10)
        self.new_game_btn.pack(side=tk.LEFT, padx=5)

        self.undo_btn = tk.Button(button_frame, text="Undo",
                                  command=self._handle_undo,
                                  font=("Arial", 12), padx=10)
        self.undo_btn.pack(side=tk.LEFT, padx=5)

        self.redo_btn = tk.Button(button_frame, text="Redo",
                                  command=self._handle_redo,
                                  font=("Arial", 12), padx=10)
        self.redo_btn.pack(side=tk.LEFT, padx=5)

        # Info frame
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=5)

        self.move_label = tk.Label(info_frame, text="Moves: 0",
                                   font=("Arial", 12))
        self.move_label.pack(side=tk.LEFT, padx=20)

        self.time_label = tk.Label(info_frame, text="Time: 0s",
                                   font=("Arial", 12))
        self.time_label.pack(side=tk.LEFT, padx=20)

        # Status label
        self.status_label = tk.Label(self.root, text="",
                                     font=("Arial", 11), fg="blue")
        self.status_label.pack(pady=5)

        # Board frame
        self.board_frame = tk.Frame(self.root, bg="#34495e", padx=10, pady=10)
        self.board_frame.pack(pady=10)

        self._create_board()

        # Start timer
        self.start_timer()

    def _create_board(self):
        """Create the puzzle board buttons."""
        # Clear existing buttons
        for widget in self.board_frame.winfo_children():
            widget.destroy()

        self.tile_buttons.clear()

        # Calculate button size based on board size
        button_size = max(60, 300 // self.size)

        for row in range(self.size):
            for col in range(self.size):
                btn = tk.Button(self.board_frame, text="",
                               width=button_size // 10,
                               height=button_size // 20,
                               font=("Arial", max(12, 24 - self.size * 2), "bold"),
                               command=lambda r=row, c=col: self._handle_tile_click(r, c))
                btn.grid(row=row, column=col, padx=2, pady=2)
                self.tile_buttons[(row, col)] = btn

    def update_board(self, board):
        """
        Update the displayed puzzle board.

        Args:
            board: 2D list representing current board state
        """
        for row in range(self.size):
            for col in range(self.size):
                value = board[row][col]
                btn = self.tile_buttons[(row, col)]

                if value == 0:
                    btn.config(text="", bg="#34495e", state=tk.DISABLED)
                else:
                    btn.config(text=str(value), bg="#3498db", fg="white",
                              state=tk.NORMAL)

    def update_move_count(self, moves: int):
        """
        Update move count display.

        Args:
            moves: Number of moves made
        """
        self.move_label.config(text=f"Moves: {moves}")

    def update_status(self, message: str, color: str = "blue"):
        """
        Update status message.

        Args:
            message: Status message to display
            color: Text color
        """
        self.status_label.config(text=message, fg=color)

    def show_message(self, title: str, message: str):
        """
        Show a message dialog.

        Args:
            title: Dialog title
            message: Message text
        """
        messagebox.showinfo(title, message)

    def show_error(self, title: str, message: str):
        """
        Show an error dialog.

        Args:
            title: Dialog title
            message: Error message
        """
        messagebox.showerror(title, message)

    def show_report(self, report_text: str):
        """
        Show statistics report in a new window.

        Args:
            report_text: Formatted report text
        """
        report_window = tk.Toplevel(self.root)
        report_window.title(f"Statistics Report - Client {self.client_id}")
        report_window.geometry("500x600")

        # Add scrollbar
        scroll = tk.Scrollbar(report_window)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        text = tk.Text(report_window, wrap=tk.WORD,
                      yscrollcommand=scroll.set, font=("Courier", 10))
        text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        scroll.config(command=text.yview)

        text.insert(tk.END, report_text)
        text.config(state=tk.DISABLED)

    def update_undo_redo_buttons(self, can_undo: bool, can_redo: bool):
        """
        Update undo/redo button states.

        Args:
            can_undo: Whether undo is available
            can_redo: Whether redo is available
        """
        self.undo_btn.config(state=tk.NORMAL if can_undo else tk.DISABLED)
        self.redo_btn.config(state=tk.NORMAL if can_redo else tk.DISABLED)

    def start_timer(self):
        """Start the game timer."""
        self.start_time = time.time()
        self.timer_running = True
        self._update_timer()

    def stop_timer(self):
        """Stop the game timer."""
        self.timer_running = False

    def get_elapsed_time(self) -> float:
        """
        Get elapsed time since game start.

        Returns:
            float: Elapsed time in seconds
        """
        return time.time() - self.start_time

    def _update_timer(self):
        """Update timer display (called periodically)."""
        if self.timer_running:
            elapsed = int(time.time() - self.start_time)
            self.time_label.config(text=f"Time: {elapsed}s")
            self.root.after(1000, self._update_timer)

    def resize_board(self, new_size: int):
        """
        Resize the puzzle board.

        Args:
            new_size: New puzzle dimension
        """
        self.size = new_size
        self._create_board()

    def _handle_tile_click(self, row: int, col: int):
        """Handle tile button click."""
        if self.on_tile_click:
            self.on_tile_click(row, col)

    def _handle_new_game(self):
        """Handle new game button click."""
        if self.on_new_game:
            self.on_new_game()

    def _handle_size_change(self):
        """Handle size radio button change."""
        new_size = self.size_var.get()
        if self.on_size_change:
            self.on_size_change(new_size)

    def _handle_undo(self):
        """Handle undo button click."""
        if self.on_undo:
            self.on_undo()

    def _handle_redo(self):
        """Handle redo button click."""
        if self.on_redo:
            self.on_redo()

    def _on_window_close(self):
        """Handle window close event."""
        if self.on_close:
            self.on_close()
        self.root.destroy()

    def run(self):
        """Start the GUI main loop."""
        self.root.mainloop()

    def destroy(self):
        """Destroy the window and remove from singleton instance."""
        # Remove singleton instance
        with self._lock:
            if self._instance is not None:
                self.__class__._instance = None
        self.root.destroy()