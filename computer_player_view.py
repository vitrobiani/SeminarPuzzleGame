"""
Computer Player GUI Module
==========================
This module implements the GUI (View) for the computer player client.

The computer automatically solves the puzzle using A* algorithm.

Classes:
    ComputerPlayerView: GUI for computer player visualization
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional, Callable, Dict
import time


class ComputerPlayerView:
    """
    GUI View for computer player puzzle solving.
    
    Implements the View component of MVC pattern for AI solver.
    Displays the puzzle being solved automatically.
    
    Attributes:
        root (tk.Tk): Main window
        size (int): Current puzzle dimension
        on_new_game (Callable): Callback for new game
        on_size_change (Callable): Callback for size change
        tile_buttons (Dict): Dictionary of tile buttons
        solving (bool): Whether currently solving
    """
    
    def __init__(self, initial_size: int = 3):
        """
        Initialize the computer player view.
        
        Args:
            initial_size: Initial puzzle dimension
        """
        self.size = initial_size
        self.root = tk.Tk()
        self.root.title("Sliding Puzzle - Computer Player")
        self.root.geometry("700x750")
        
        # Callbacks (set by controller)
        self.on_new_game: Optional[Callable] = None
        self.on_size_change: Optional[Callable] = None
        self.on_close: Optional[Callable] = None
        
        # UI elements
        self.tile_buttons: Dict = {}
        self.move_label: Optional[tk.Label] = None
        self.status_label: Optional[tk.Label] = None
        self.progress_label: Optional[tk.Label] = None
        
        # State
        self.solving = False
        
        self._create_ui()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
    
    def _create_ui(self):
        """Create all UI elements."""
        # Top frame for controls
        control_frame = tk.Frame(self.root, pady=10)
        control_frame.pack()
        
        # Title
        tk.Label(control_frame, text="Computer Player (A* Solver)", 
                font=("Arial", 14, "bold")).pack()
        
        # Size selection
        size_frame = tk.Frame(control_frame)
        size_frame.pack(pady=5)
        
        tk.Label(size_frame, text="Board Size:").pack(side=tk.LEFT, padx=5)
        
        self.size_var = tk.IntVar(value=self.size)
        for size in [3, 4, 5, 6, 7]:
            tk.Radiobutton(size_frame, text=f"{size}x{size}", 
                          variable=self.size_var, value=size,
                          command=self._handle_size_change).pack(side=tk.LEFT)
        
        # Button frame
        button_frame = tk.Frame(control_frame)
        button_frame.pack(pady=5)
        
        self.new_game_btn = tk.Button(button_frame, text="New Game & Solve", 
                                      command=self._handle_new_game,
                                      font=("Arial", 12), bg="#4CAF50", 
                                      fg="white", padx=10)
        self.new_game_btn.pack(side=tk.LEFT, padx=5)
        
        # Speed control frame
        speed_frame = tk.Frame(control_frame)
        speed_frame.pack(pady=5)

        tk.Label(speed_frame, text="Animation Speed:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

        # Speed slider (0.1x to 10x speed)
        self.speed_var = tk.DoubleVar(value=1.0)
        self.speed_slider = tk.Scale(
            speed_frame,
            from_=0.1,
            to=10.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.speed_var,
            length=200,
            command=self._on_speed_change
        )
        self.speed_slider.pack(side=tk.LEFT, padx=5)

        self.speed_label = tk.Label(speed_frame, text="1.0x", font=("Arial", 10), width=6)
        self.speed_label.pack(side=tk.LEFT, padx=5)

        # Info frame
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=5)

        self.move_label = tk.Label(info_frame, text="Moves: 0",
                                   font=("Arial", 12))
        self.move_label.pack(pady=2)

        self.progress_label = tk.Label(info_frame, text="",
                                       font=("Arial", 11))
        self.progress_label.pack(pady=2)

        # Status label
        self.status_label = tk.Label(self.root, text="Click 'New Game & Solve' to start",
                                     font=("Arial", 11), fg="blue")
        self.status_label.pack(pady=5)

        # Board frame
        self.board_frame = tk.Frame(self.root, bg="#34495e", padx=10, pady=10)
        self.board_frame.pack(pady=10)

        self._create_board()

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
                               state=tk.DISABLED)
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
                    btn.config(text="", bg="#34495e")
                else:
                    btn.config(text=str(value), bg="#e74c3c", fg="white")

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

    def update_progress(self, message: str):
        """
        Update progress message during solving.

        Args:
            message: Progress message
        """
        self.progress_label.config(text=message)

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

    def set_solving(self, solving: bool):
        """
        Set solving state and update UI accordingly.

        Args:
            solving: Whether currently solving
        """
        self.solving = solving
        if solving:
            self.new_game_btn.config(state=tk.DISABLED)
        else:
            self.new_game_btn.config(state=tk.NORMAL)

    def resize_board(self, new_size: int):
        """
        Resize the puzzle board.

        Args:
            new_size: New puzzle dimension
        """
        self.size = new_size
        self._create_board()

    def _handle_new_game(self):
        """Handle new game button click."""
        if self.on_new_game:
            self.on_new_game()

    def _handle_size_change(self):
        """Handle size radio button change."""
        new_size = self.size_var.get()
        if self.on_size_change:
            self.on_size_change(new_size)

    def _on_speed_change(self, value):
        """Handle speed slider change."""
        speed = float(value)
        self.speed_label.config(text=f"{speed:.1f}x")

    def get_animation_speed(self) -> float:
        """
        Get current animation speed multiplier.

        Returns:
            float: Speed multiplier (0.1 to 10.0)
        """
        return self.speed_var.get()

    def _on_window_close(self):
        """Handle window close event."""
        if self.on_close:
            self.on_close()
        self.root.destroy()

    def run(self):
        """Start the GUI main loop."""
        self.root.mainloop()

    def destroy(self):
        """Destroy the window."""
        self.root.destroy()