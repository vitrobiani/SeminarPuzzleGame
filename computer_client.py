"""
Computer Player Client Launcher
===============================
This script launches the computer player client instance.

The client is launched from the server GUI.
Only one computer player can be active at a time (Singleton).
"""

from computer_player_controller import ComputerPlayerController


def main():
    """Main entry point for computer player client."""
    # Create and run controller
    controller = ComputerPlayerController()
    controller.run()


if __name__ == "__main__":
    main()
