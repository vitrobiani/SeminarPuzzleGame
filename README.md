# Sliding Puzzle Game System
## Programming Languages Seminar Project

A comprehensive sliding puzzle game system implementing client-server architecture with both human and AI players.

---

## 📋 Project Overview

This system implements a complete sliding puzzle game (N-puzzle) with the following features:
- **Client-Server Architecture**: Multiple clients connecting to a central server
- **Human Player Mode**: Interactive GUI for manual puzzle solving
- **Computer Player Mode**: AI solver using A* algorithm with Manhattan distance heuristic
- **Design Patterns**: MVC, Singleton, Memento
- **Statistics Tracking**: Comprehensive game statistics and reports
- **Solvability Detection**: Automatic detection of unsolvable puzzle configurations

---

## 🎯 Features

### Core Functionality
- ✅ Support for 4 board sizes: 3×3, 4×4, 5×5, 6×6
- ✅ Automatic solvability checking using inversion counting
- ✅ Undo/Redo functionality (Memento pattern)
- ✅ Real-time move and time tracking
- ✅ Statistics and reporting per client
- ✅ Server logging of all activities

### Human Player Client
- Interactive tile clicking interface
- Dynamic board resizing during gameplay
- Undo/Redo support for unlimited moves
- Real-time timer and move counter
- Statistics report showing:
  - Total games played per size
  - Unsolvable puzzles encountered
  - Abandoned games
  - Successfully solved puzzles
  - Average solving time
  - Average number of moves

### Computer Player Client
- Automatic puzzle solving using A* algorithm
- Manhattan distance heuristic for optimal pathfinding
- Visual animation of solution execution
- 120-second timeout protection
- Node expansion statistics
- Only one computer player can run at a time (Singleton)

### Server
- Central management console with GUI
- Launch human and computer clients from server interface
- Real-time activity logging
- Client connection monitoring
- Thread-safe client handling

---

## 🏗️ Architecture

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

## 📁 Project Structure

```
sliding_puzzle_project/
│
├── server.py                      # Main server with GUI (Singleton)
├── human_client.py                # Human player launcher
├── computer_client.py             # Computer player launcher
│
├── puzzle_model.py                # Core puzzle logic (Model)
├── human_player_view.py           # Human player GUI (View)
├── computer_player_view.py        # Computer player GUI (View)
├── human_player_controller.py     # Human player logic (Controller)
├── computer_player_controller.py  # Computer player logic (Controller)
│
├── astar_solver.py                # A* algorithm implementation
├── memento.py                     # Memento pattern for undo/redo
├── statistics.py                  # Statistics tracking and reporting
│
└── README.md                      # This file
```

---

## 🚀 How to Run

### Prerequisites
- Python 3.10.x or higher
- tkinter (usually included with Python)
- No external dependencies required!

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
1. Select board size (3×3, 4×4, 5×5, or 6×6)
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

## 🧮 Algorithm Details

### Solvability Checking
The system uses inversion counting to determine if a puzzle configuration is solvable:

**For odd-sized boards (3×3, 5×5):**
- Puzzle is solvable if the number of inversions is even

**For even-sized boards (4×4, 6×6):**
- Puzzle is solvable if (inversions + empty_row_from_bottom) is odd

An **inversion** is when a larger number appears before a smaller number when reading the board left-to-right, top-to-bottom (excluding the empty tile).

### A* Algorithm
The computer player uses A* pathfinding with:
- **Heuristic**: Manhattan distance (sum of distances of each tile from its goal position)
- **Cost Function**: f(n) = g(n) + h(n)
  - g(n): moves made so far
  - h(n): Manhattan distance to goal
- **Timeout**: 120 seconds maximum
- **Optimization**: Closed set to avoid revisiting states

---

## 📊 Statistics and Reporting

Each human player client maintains statistics including:
- Total games played per board size
- Number of unsolvable puzzles encountered
- Number of abandoned games
- Number of successfully solved puzzles
- Average solving time (seconds)
- Average number of moves

Statistics are:
- Saved automatically to JSON files (`stats_client_N.json`)
- Persistent across sessions
- Viewable via "Show Report" button

---

## 🔧 Technical Implementation

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

## 🎓 Learning Objectives Achieved

1. **Algorithm Implementation**:
   - Inversion counting for solvability
   - A* pathfinding with heuristics
   - Manhattan distance calculation

2. **Design Patterns**:
   - MVC architecture separation
   - Singleton for single-instance components
   - Memento for state management

3. **Network Programming**:
   - Client-server architecture
   - Socket programming
   - Thread management
   - Data serialization

4. **GUI Development**:
   - tkinter interface design
   - Event-driven programming
   - Responsive layouts

5. **Software Engineering**:
   - Modular code organization
   - Comprehensive documentation
   - Error handling
   - State management

---

## 📝 Python Documentation Standards

All code follows Python documentation standards (PEP 257):
- Module docstrings explaining purpose
- Class docstrings with attributes
- Function/method docstrings with Args, Returns, Raises
- Inline comments for complex logic
- Type hints for better code clarity

Example:
```python
def move(self, tile_pos: Tuple[int, int]) -> bool:
    """
    Move a tile into the empty space.
    
    Args:
        tile_pos: Position (row, col) of the tile to move
        
    Returns:
        bool: True if move was valid and executed, False otherwise
    """
```

---

## 🐛 Error Handling

The system handles:
- ✅ Unsolvable puzzle configurations (detected and reported)
- ✅ Server connection failures (graceful degradation)
- ✅ Client disconnections (automatic cleanup)
- ✅ Solver timeouts (120-second limit)
- ✅ Invalid moves (ignored with no errors)
- ✅ Window close events (statistics saved)

---

## 💡 Usage Tips

1. **For Testing Solvability**: The system generates truly random puzzles, so you'll occasionally see unsolvable configurations - this is expected!

2. **For Best Computer Performance**: Smaller boards (3×3, 4×4) solve quickly. Larger boards may take longer or timeout.

3. **Statistics Persistence**: Your statistics are saved automatically. Even if you close and reopen a client with the same ID, stats will be preserved.

4. **Server Log**: Keep an eye on the server log to see all system activities in real-time.

5. **Multiple Human Players**: You can launch multiple human player clients - each gets its own ID and maintains separate statistics.

---

## 🔮 Future Enhancements (Optional)

Potential improvements that could be added:
- Different heuristics (Linear Conflict, Pattern Database)
- Difficulty selection (guaranteed solvability)
- Leaderboards across all clients
- Save/Load game state
- Customizable themes
- Sound effects
- Network play across different computers

---

## 👥 Development

**Project Type**: Programming Languages Seminar  
**Language**: Python 3.10.x  
**IDE**: PyCharm Community Edition  
**Pattern**: Client-Server with Threads  

---

## 📄 License

This project is created for educational purposes as part of a university seminar course.

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
- [x] 120-second timeout for solver
- [x] Statistics tracking and reporting
- [x] Server logging
- [x] Comprehensive Python documentation
- [x] Single .py file execution (server.py only)

---

## 🎉 Success Criteria Met

✓ The entire system runs from a single `server.py` execution  
✓ All clients are launched from the server GUI  
✓ No console input/output required (except debug prints)  
✓ All three design patterns properly implemented  
✓ Full GUI interface for all interactions  
✓ Complete statistics and reporting  
✓ Proper solvability detection  
✓ Working A* solver with heuristic  
✓ Thread-safe client-server communication  
✓ Comprehensive documentation following Python standards  

---

**Good Luck with Your Demonstration! 🚀**
