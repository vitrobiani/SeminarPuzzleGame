"""
Server Module
=============
This module implements the main server with GUI for managing clients.

Implements Singleton pattern to ensure only one server instance.

Classes:
    PuzzleServer: Main server managing clients and logging
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import socket
import threading
import subprocess
import sys
import pickle
from datetime import datetime
from typing import Optional, Dict
import os
import json
import glob


class PuzzleServer:
    """
    Main server for sliding puzzle system (Singleton).
    
    Manages client connections and provides logging functionality.
    Only one server instance can exist at a time.
    
    Attributes:
        _instance: Singleton instance
        root (tk.Tk): Server GUI window
        log_text (scrolledtext.ScrolledText): Log display
        server_socket (socket.socket): Server socket for clients
        running (bool): Whether server is running
        clients (Dict): Connected clients
        next_client_id (int): Next available client ID
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern implementation."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        """Initialize server (only once due to Singleton)."""
        if self._initialized:
            return
        
        self._initialized = True
        
        # Server state
        self.running = False
        self.server_socket: Optional[socket.socket] = None
        self.clients: Dict[str, socket.socket] = {}
        self.next_client_id = 1
        self.human_client_count = 0
        self.human_client_active = False  # Track if human player is active
        self.computer_client_active = False
        self.statistics_active = False # Track if statistics window is open

        # GUI
        self.root = tk.Tk()
        self.root.title("Sliding Puzzle Server")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.shutdown)

        self._create_ui()

        # Start server
        self.start_server()

    def _create_ui(self):
        """Create server GUI."""
        # Title
        title_frame = tk.Frame(self.root, bg="#2c3e50", pady=15)
        title_frame.pack(fill=tk.X)

        tk.Label(title_frame, text="Sliding Puzzle Server",
                font=("Arial", 18, "bold"), bg="#2c3e50", fg="white").pack()

        tk.Label(title_frame, text="Managing Client Connections",
                font=("Arial", 11), bg="#2c3e50", fg="#ecf0f1").pack()

        # Button frame
        button_frame = tk.Frame(self.root, pady=10)
        button_frame.pack()

        # Launch buttons
        self.human_btn = tk.Button(button_frame, text="Launch Human Player",
                                   command=self.launch_human_client,
                                   font=("Arial", 12, "bold"), bg="#27ae60",
                                   fg="white", padx=20, pady=10)
        self.human_btn.pack(side=tk.LEFT, padx=10)

        self.computer_btn = tk.Button(button_frame, text="Launch Computer Player",
                                      command=self.launch_computer_client,
                                      font=("Arial", 12, "bold"), bg="#e74c3c",
                                      fg="white", padx=20, pady=10)
        self.computer_btn.pack(side=tk.LEFT, padx=10)

        self.stats_btn = tk.Button(button_frame, text="Show Statistics",
                                   command=self.show_statistics,
                                   font=("Arial", 12, "bold"), bg="#3498db",
                                   fg="white", padx=20, pady=10)
        self.stats_btn.pack(side=tk.LEFT, padx=10)

        # Status frame
        status_frame = tk.Frame(self.root, pady=5)
        status_frame.pack()

        self.status_label = tk.Label(status_frame, text="Server Status: Running",
                                     font=("Arial", 11), fg="green")
        self.status_label.pack()

        self.client_count_label = tk.Label(status_frame,
                                           text="Connected Clients: 0 Human, 0 Computer",
                                           font=("Arial", 10))
        self.client_count_label.pack()

        # Log frame
        log_frame = tk.Frame(self.root)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(log_frame, text="Server Log:", font=("Arial", 11, "bold")).pack(anchor=tk.W)

        self.log_text = scrolledtext.ScrolledText(log_frame,
                                                  wrap=tk.WORD,
                                                  font=("Courier", 9),
                                                  bg="#f8f9fa",
                                                  fg="#2c3e50")
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Clear log button
        tk.Button(self.root, text="Clear Log", command=self.clear_log,
                 font=("Arial", 10)).pack(pady=5)

    def start_server(self):
        """Start the server socket and accept connections."""
        try:
            # Create TCP socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Allow reusing address (prevents "address already in use" error)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Bind to localhost:5000
            self.server_socket.bind(('localhost', 5000))
            # Listen for up to 2 pending connections
            self.server_socket.listen(2)

            self.running = True
            self.log("Server started on localhost:5000")

            # Start accepting clients in separate thread
            accept_thread = threading.Thread(target=self._accept_clients, daemon=True)
            accept_thread.start()

        except Exception as e:
            self.log(f"Error starting server: {e}", "ERROR")
            self.status_label.config(text="Server Status: Error", fg="red")

    def _accept_clients(self):
        """Accept client connections (runs in separate thread)."""
        while self.running:
            try:
                # BLOCKING CALL - waits for client to connect
                client_socket, address = self.server_socket.accept()

                # Handle client in separate thread
                # Create NEW thread for this client
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket,),
                    daemon=True
                )
                client_thread.start()

            except Exception as e:
                if self.running:
                    self.log(f"Error accepting client: {e}", "ERROR")

    def _handle_client(self, client_socket: socket.socket):
        """
        Handle individual client connection.

        Args:
            client_socket: Client's socket connection
        """
        try:
            # Receive client info
            # Receive 4KB of data
            data = client_socket.recv(4096)
            # Deserialize using pickle
            client_info = pickle.loads(data)

            # Extract info
            client_type = client_info.get('type', 'unknown') # 'human' or 'computer'
            client_id = client_info.get('client_id', 'unknown')

            # Store client socket
            self.clients[str(client_id)] = client_socket

            if client_type == 'human':
                self.human_client_count += 1
                self.human_client_active = True
            elif client_type == 'computer':
                self.computer_client_active = True

            self.update_client_count()

            # Receive messages from client
            while self.running:
                try:
                    data = client_socket.recv(4096)
                    if not data:
                        break # Client disconnected

                    message = pickle.loads(data)

                    if message.get('action') == 'log':
                        self.log(message.get('message', ''))

                except:
                    break

        except Exception as e:
            self.log(f"Error handling client: {e}", "ERROR")

        finally:
            # Clean up
            if str(client_id) in self.clients:
                del self.clients[str(client_id)]

                if client_type == 'human':
                    self.human_client_count = max(0, self.human_client_count - 1)
                    self.human_client_active = False
                elif client_type == 'computer':
                    self.computer_client_active = False

                self.update_client_count()

            try:
                client_socket.close()
            except:
                pass

    def launch_human_client(self):
        """Launch a new human player client."""
        if self.human_client_active:
            self.log("Human player already active!", "WARNING")
            return

        try:
            client_id = self.next_client_id
            self.next_client_id += 1

            # Launch client in separate process
            script_path = os.path.join(os.path.dirname(__file__), "human_client.py")

            subprocess.Popen([sys.executable, script_path, str(client_id)])

            self.log(f"Launched Human Player Client {client_id}")

        except Exception as e:
            self.log(f"Error launching human client: {e}", "ERROR")

    def launch_computer_client(self):
        """Launch computer player client."""
        if self.computer_client_active:
            self.log("Computer player already active!", "WARNING")
            return

        try:
            # Launch client in separate process
            script_path = os.path.join(os.path.dirname(__file__), "computer_client.py")

            subprocess.Popen([sys.executable, script_path])

            self.log("Launched Computer Player Client")

        except Exception as e:
            self.log(f"Error launching computer client: {e}", "ERROR")

    def log(self, message: str, level: str = "INFO"):
        """
        Add message to server log.

        Args:
            message: Log message
            level: Log level (INFO, WARNING, ERROR)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"

        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)

        # Also print to console
        print(log_entry.strip())

    def update_client_count(self):
        """Update client count display."""
        human_text = "1 Human" if self.human_client_active else "0 Human"
        computer_text = "1 Computer" if self.computer_client_active else "0 Computer"
        self.client_count_label.config(
            text=f"Connected Clients: {human_text}, {computer_text}"
        )

    def clear_log(self):
        """Clear the server log."""
        self.log_text.delete(1.0, tk.END)
        self.log("Log cleared")

    def show_statistics(self):
        """Show combined statistics for all players."""
        if self.statistics_active:
            self.log("Statistics window already open!", "WARNING")
            return
        try:
            self.statistics_active = True
            # Find all stats files (both human and computer)
            human_stats_files = glob.glob("stats_client_*.json")
            computer_stats_file = "stats_computer.json"

            if not human_stats_files and not os.path.exists(computer_stats_file):
                messagebox.showinfo("Statistics", "No statistics available yet.\nPlay some games to generate statistics!")
                self.statistics_active = False
                return

            # Separate human and computer statistics
            human_stats_by_size = {}
            computer_stats_by_size = {}

            # Load human player statistics
            for stats_file in sorted(human_stats_files):
                try:
                    with open(stats_file, 'r') as f:
                        data = json.load(f)

                    stats_data = data.get('stats', {})

                    for size_str, size_stats in stats_data.items():
                        size = int(size_str)

                        if size not in human_stats_by_size:
                            human_stats_by_size[size] = {
                                'solved_games': 0,
                                'total_time': 0.0,
                                'total_moves': 0,
                                'games_list': []
                            }

                        human_stats_by_size[size]['solved_games'] += size_stats.get('solved_games', 0)
                        human_stats_by_size[size]['total_time'] += size_stats.get('total_time', 0.0)
                        human_stats_by_size[size]['total_moves'] += size_stats.get('total_moves', 0)
                        human_stats_by_size[size]['games_list'].extend(size_stats.get('games_list', []))

                except Exception as e:
                    self.log(f"Error reading {stats_file}: {e}", "WARNING")

            # Load computer player statistics
            if os.path.exists(computer_stats_file):
                try:
                    with open(computer_stats_file, 'r') as f:
                        data = json.load(f)

                    stats_data = data.get('stats', {})

                    for size_str, size_stats in stats_data.items():
                        size = int(size_str)

                        computer_stats_by_size[size] = {
                            'solved_games': size_stats.get('solved_games', 0),
                            'total_time': size_stats.get('total_time', 0.0),
                            'total_moves': size_stats.get('total_moves', 0),
                            'games_list': size_stats.get('games_list', [])
                        }

                except Exception as e:
                    self.log(f"Error reading {computer_stats_file}: {e}", "WARNING")

            # Format report
            report = self._format_statistics_report(human_stats_by_size, computer_stats_by_size)

            # Display in new window
            self._show_statistics_window(report)

            self.log("Display statistics")

        except Exception as e:
            self.log(f"Error showing statistics: {e}", "ERROR")
            messagebox.showerror("Error", f"Failed to load statistics:\n{e}")
            self.statistics_active = False

    def _format_statistics_report(self, human_stats_by_size, computer_stats_by_size):
        """
        Format simplified statistics report.

        Args:
            human_stats_by_size: Human player statistics by puzzle size
            computer_stats_by_size: Computer player statistics by puzzle size

        Returns:
            str: Formatted report
        """
        report_lines = ["=" * 80]
        report_lines.append("GAME STATISTICS - ALL PLAYERS")
        report_lines.append("=" * 80)
        report_lines.append("")

        # Get all puzzle sizes
        all_sizes = sorted(set(list(human_stats_by_size.keys()) + list(computer_stats_by_size.keys())))

        if not all_sizes:
            report_lines.append("No games completed yet.")
            report_lines.append("=" * 80)
            return "\n".join(report_lines)

        # Statistics for each board size
        for size in all_sizes:
            human_stats = human_stats_by_size.get(size, {'solved_games': 0, 'total_time': 0.0, 'total_moves': 0, 'games_list': []})
            computer_stats = computer_stats_by_size.get(size, {'solved_games': 0, 'total_time': 0.0, 'total_moves': 0, 'games_list': []})

            # Skip if no games were solved for this size
            if human_stats['solved_games'] == 0 and computer_stats['solved_games'] == 0:
                continue

            report_lines.append(f"{size}x{size} PUZZLE")
            report_lines.append("-" * 80)

            # Human player stats
            if human_stats['solved_games'] > 0:
                avg_time = human_stats['total_time'] / human_stats['solved_games']
                avg_moves = human_stats['total_moves'] / human_stats['solved_games']
                report_lines.append(f"  Human Players: {human_stats['solved_games']} games won")

                # List individual games
                for i, game in enumerate(human_stats['games_list'], 1):
                    report_lines.append(f"    Game {i}: {game['moves']} moves, {game['time']:.2f} seconds")

                report_lines.append("")
                report_lines.append(f"    Average: {avg_moves:.2f} moves, {avg_time:.2f} seconds")
            else:
                report_lines.append(f"  Human Players:    No games won yet")

            report_lines.append("")

            # Computer player stats
            if computer_stats['solved_games'] > 0:
                avg_time = computer_stats['total_time'] / computer_stats['solved_games']
                avg_moves = computer_stats['total_moves'] / computer_stats['solved_games']
                report_lines.append(f"  Computer Player: {computer_stats['solved_games']} games won")

                # List individual games
                for i, game in enumerate(computer_stats['games_list'], 1):
                    report_lines.append(f"    Game {i}: {game['moves']} moves, {game['time']:.2f} seconds")

                report_lines.append("")
                report_lines.append(f"    Average: {avg_moves:.2f} moves, {avg_time:.2f} seconds")
            else:
                report_lines.append(f"  Computer Player:  No games won yet")

            # Overall average (combining both human and computer)
            total_solved = human_stats['solved_games'] + computer_stats['solved_games']
            if total_solved > 0:
                total_time = human_stats['total_time'] + computer_stats['total_time']
                total_moves = human_stats['total_moves'] + computer_stats['total_moves']
                overall_avg_time = total_time / total_solved
                overall_avg_moves = total_moves / total_solved

                report_lines.append("")
                report_lines.append(f"  Overall Average (Both Players):")
                report_lines.append(f"    Total Games:    {total_solved}")
                report_lines.append(f"    Average:        {overall_avg_moves:.2f} moves, {overall_avg_time:.2f} seconds")

            report_lines.append("")
            report_lines.append("")

        report_lines.append("=" * 80)

        return "\n".join(report_lines)

    def _show_statistics_window(self, report_text):
        """
        Display statistics in a new window.

        Args:
            report_text: Formatted statistics report
        """
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Statistics - All Players")
        stats_window.geometry("800x700")

        # Add scrollbar
        scroll = tk.Scrollbar(stats_window)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        stats_window.protocol("WM_DELETE_WINDOW", lambda: [stats_window.destroy(), self._close_statistics_window()])

        # Add text widget
        text = tk.Text(stats_window, wrap=tk.WORD,
                      yscrollcommand=scroll.set, font=("Courier", 10))
        text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        scroll.config(command=text.yview)

        # Insert report
        text.insert(tk.END, report_text)
        text.config(state=tk.DISABLED)

        # Button frame for refresh and close buttons
        button_frame = tk.Frame(stats_window)
        button_frame.pack(pady=10)

        # Add refresh button
        refresh_btn = tk.Button(button_frame, text="Refresh",
                               command=lambda: self._refresh_statistics(text),
                               font=("Arial", 11), bg="#27ae60",
                               fg="white", padx=20, pady=5)
        refresh_btn.pack(side=tk.LEFT, padx=10)

        # Add close button
        close_btn = tk.Button(button_frame, text="Close",
                             command=lambda: [stats_window.destroy(), self._close_statistics_window()],
                             font=("Arial", 11), bg="#95a5a6",
                             fg="white", padx=20, pady=5)
        close_btn.pack(side=tk.LEFT, padx=10)

    def _refresh_statistics(self, text_widget):
        """
        Refresh the statistics display with latest data.

        Args:
            text_widget: The text widget to update
        """
        try:
            # Reload statistics from files
            human_stats_files = glob.glob("stats_client_*.json")
            computer_stats_file = "stats_computer.json"

            human_stats_by_size = {}
            computer_stats_by_size = {}

            # Load human player statistics
            for stats_file in sorted(human_stats_files):
                try:
                    with open(stats_file, 'r') as f:
                        data = json.load(f)

                    stats_data = data.get('stats', {})

                    for size_str, size_stats in stats_data.items():
                        size = int(size_str)

                        if size not in human_stats_by_size:
                            human_stats_by_size[size] = {
                                'solved_games': 0,
                                'total_time': 0.0,
                                'total_moves': 0,
                                'games_list': []
                            }

                        human_stats_by_size[size]['solved_games'] += size_stats.get('solved_games', 0)
                        human_stats_by_size[size]['total_time'] += size_stats.get('total_time', 0.0)
                        human_stats_by_size[size]['total_moves'] += size_stats.get('total_moves', 0)
                        human_stats_by_size[size]['games_list'].extend(size_stats.get('games_list', []))

                except Exception as e:
                    self.log(f"Error reading {stats_file}: {e}", "WARNING")

            # Load computer player statistics
            if os.path.exists(computer_stats_file):
                try:
                    with open(computer_stats_file, 'r') as f:
                        data = json.load(f)

                    stats_data = data.get('stats', {})

                    for size_str, size_stats in stats_data.items():
                        size = int(size_str)

                        computer_stats_by_size[size] = {
                            'solved_games': size_stats.get('solved_games', 0),
                            'total_time': size_stats.get('total_time', 0.0),
                            'total_moves': size_stats.get('total_moves', 0),
                            'games_list': size_stats.get('games_list', [])
                        }

                except Exception as e:
                    self.log(f"Error reading {computer_stats_file}: {e}", "WARNING")

            # Format the new report
            report = self._format_statistics_report(human_stats_by_size, computer_stats_by_size)

            # Update the text widget
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, report)
            text_widget.config(state=tk.DISABLED)

            self.log("Statistics refreshed")

        except Exception as e:
            self.log(f"Error refreshing statistics: {e}", "ERROR")

    def _close_statistics_window(self):
        """Callback when statistics window is closed."""
        self.statistics_active = False

    def shutdown(self):
        """Shutdown the server."""
        self.log("Shutting down server...")
        self.running = False

        # Close all client connections
        for client_socket in list(self.clients.values()):
            try:
                client_socket.close()
            except:
                pass

        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass

        self.root.destroy()

    def run(self):
        """Run the server."""
        self.root.mainloop()


def main():
    """Main entry point for server."""
    server = PuzzleServer()
    server.run()


if __name__ == "__main__":
    main()