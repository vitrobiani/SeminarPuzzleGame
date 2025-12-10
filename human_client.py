"""
Human Player Client Launcher
============================
This script launches a human player client instance.

The client is launched from the server GUI.
"""

import sys
from human_player_controller import HumanPlayerController


def main():
    """Main entry point for human player client."""
    # Get client ID from command line argument
    if len(sys.argv) > 1:
        client_id = int(sys.argv[1])
    else:
        client_id = 1
    
    # Create and run controller
    controller = HumanPlayerController(client_id=client_id)
    controller.run()


if __name__ == "__main__":
    main()
