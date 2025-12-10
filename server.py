"""
Server Module
=============
This module implements the main server with GUI for managing clients.

Implements Singleton pattern to ensure only one server instance.

Classes:
    PuzzleServer: Main server managing clients and logging
"""

import tkinter as tk
from tkinter import scrolledtext
import socket
import threading
import subprocess
import sys
import pickle
from datetime import datetime
from typing import Optional, Dict
import os


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
            # Listen for up to 5 pending connections
            self.server_socket.listen(5)

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