# Sliding Puzzle Game System
## Programming Languages Seminar Project

A comprehensive sliding puzzle game system implementing client-server architecture with both human and AI players.

---

## Project Overview

This system implements a complete sliding puzzle game (N-puzzle) with the following features:
- **Client-Server Architecture**: Multiple clients connecting to a central server
- **Human Player Mode**: Interactive GUI for manual puzzle solving
- **Computer Player Mode**: AI solver using A* algorithm with Manhattan distance heuristic
- **Design Patterns**: MVC, Singleton, Memento
- **Statistics Tracking**: Comprehensive game statistics and reports
- **Solvability Detection**: Automatic detection of unsolvable puzzle configurations

---

### Human Player Client
- Interactive tile clicking interface
- Dynamic board resizing during gameplay
- Undo/Redo support for unlimited moves
- timer and move counter
- Statistics report showing:
  - Total games played per size
  - Unsolvable puzzles encountered
  - Abandoned games
  - Successfully solved puzzles
  - Average solving time
  - Average number of moves

### Computer Player Client
- Automatic puzzle solving using a BFS algorithm or "Human like" algorithm
- Manhattan distance heuristic for optimal pathfinding
- Visual animation of solution execution
- 120-second timeout protection
- Node expansion statistics

### Server
- Central management console with GUI
- Launch human and computer clients from server interface
- Real-time activity logging
- Client connection monitoring
- Thread-safe client handling
- Statistics page showing overall performance

---

## Architecture

### Design Patterns Implemented

#### 1. Model-View-Controller (MVC)
- **Model**: `puzzle_model.py` - Core game logic and state
- **View**: `human_player_view.py`, `computer_player_view.py` - GUI interfaces
- **Controller**: `human_player_controller.py`, `computer_player_controller.py` - Business logic

#### 2. Singleton
- **Server**: Only one server instance can run
- **Client Windows**: Only one window per human client, one computer client total

#### 3. Memento
- **Implementation**: `memento.py`
- **Usage**: Undo/Redo functionality in human player mode
- **Caretaker**: Manages state history

### Network Architecture
- **Protocol**: TCP/IP sockets
- **Communication**: Pickle serialization for data transfer
- **Threading**: Separate threads for each client connection
- **Server Port**: 5000 (localhost)

---

## How to Run

### Prerequisites
- Python 3.10.x or higher
- tkinter 

### Starting the System

1. **Run the Server** (this is the ONLY file you need to execute):
   ```bash
   python server.py
   ```

2. **From the Server GUI**:
   - Click "Launch Human Player" to start a human player client
   - Click "Launch Computer Player" to start the AI solver
   - Multiple human players can be launched
   - Only one computer player can be active at a time

### Playing the Game

#### Human Player:
1. Select board size (3×3 - 10×10)
2. Click "New Game" to generate a puzzle
3. Click on tiles adjacent to the empty space to move them
4. Use "Undo" and "Redo" to navigate move history
5. Click "Show Report" to view your statistics
6. The system will detect if a puzzle is unsolvable

#### Computer Player:
1. Select board size
2. Click "New Game & Solve"
3. Watch the AI solve the puzzle automatically
4. The solver uses A* with Manhattan distance heuristic
5. Solution is animated with optimal path visualization

---

## Statistics and Reporting

Each human player client maintains statistics including:
- Total games played per board size
- Number of unsolvable puzzles encountered
- Number of abandoned games
- Number of successfully solved puzzles
- Average solving time (seconds)
- Average number of moves

Statistics are:
- Saved automatically to JSON files 
- Persistent across sessions
- Viewable via "Show Report" button

---

## Technical Implementation

### Threading
- Server accepts connections in a separate thread
- Each client connection is handled in its own thread
- Computer solver runs in a separate thread to keep GUI responsive

### Network Communication
- **Pickle Protocol**: Python objects serialized for network transmission
- **Message Types**:
  - Client registration (type, client_id)
  - Log messages (action: 'log', message)
- **Error Handling**: Graceful connection failures and disconnections

### GUI Implementation
- **Framework**: tkinter
- **Responsive Design**: Adaptive button sizes based on board dimensions
- **Real-time Updates**: Timer updates every second
- **No Pop-ups**: All notifications in main window (as required)

---

## Error Handling

The system handles:
- ✅ Unsolvable puzzle configurations (detected and reported)
- ✅ Server connection failures (graceful degradation)
- ✅ Client disconnections (automatic cleanup)
- ✅ Solver timeouts (120-second limit)
- ✅ Invalid moves (ignored with no errors)
- ✅ Window close events (statistics saved)

---

## ✅ Requirements Checklist

- [x] 4 board sizes supported (3×3, 4×4, 5×5, 6×6)
- [x] Solvability detection with proper algorithm
- [x] MVC pattern implemented
- [x] Memento pattern for undo/redo
- [x] Singleton pattern for server and computer client
- [x] Client-server architecture
- [x] Threading for concurrent clients
- [x] Full GUI (no console I/O)
- [x] Server launches clients via GUI
- [x] A* algorithm for computer player
- [x] Human-like algorithm for computer player
- [x] 120-second timeout for solver
- [x] Statistics tracking and reporting
- [x] Server logging
- [x] Comprehensive Python documentation
- [x] Single .py file execution (server.py only)
