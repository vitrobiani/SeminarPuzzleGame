# Quick Start Guide - Sliding Puzzle System

## 🚀 Running the System (3 Easy Steps)

### Step 1: Navigate to Project Directory
```bash
cd sliding_puzzle_project
```

### Step 2: Run the Server
```bash
python server.py
```

### Step 3: Use the Server GUI
- Click **"Launch Human Player"** for interactive play
- Click **"Launch Computer Player"** to watch AI solve puzzles

That's it! ✅

---

## 🎮 Quick Controls

### Human Player:
- **Click tiles** next to empty space to move
- **New Game** - Generate new puzzle
- **Undo/Redo** - Navigate move history
- **Show Report** - View your statistics
- **Board Size** - Switch between 3×3, 4×4, 5×5, 6×6

### Computer Player:
- **New Game & Solve** - Watch AI solve automatically
- **Board Size** - Choose puzzle complexity

---

## 📖 What to Expect

### First Launch:
1. Server window opens with two buttons
2. Click "Launch Human Player" → New window opens
3. Click "New Game" in the client window
4. Start playing!

### If Puzzle Says "UNSOLVABLE":
- This is **normal and expected**!
- Random generation can create unsolvable puzzles
- Just click "New Game" again
- The system correctly detects this using mathematical analysis

### Computer Player:
- Solves most 3×3 puzzles instantly
- 4×4 puzzles take a few seconds
- 5×5 and 6×6 may take longer or timeout (120s limit)

---

## 🔍 Troubleshooting

### "Connection refused" error:
- Make sure server is running first
- Server must stay open while clients run

### Client won't launch:
- Check that all .py files are in the same directory
- Make sure Python 3.10+ is installed

### Tkinter not found:
```bash
# Ubuntu/Debian:
sudo apt-get install python3-tk

# Fedora:
sudo dnf install python3-tkinter
```

---

## 📊 File Structure Quick Reference

```
sliding_puzzle_project/
├── server.py                    ← START HERE (run this file)
├── human_client.py              (launched by server)
├── computer_client.py           (launched by server)
├── puzzle_model.py              (game logic)
├── human_player_view.py         (human GUI)
├── computer_player_view.py      (computer GUI)
├── human_player_controller.py   (human controller)
├── computer_player_controller.py (computer controller)
├── astar_solver.py              (AI solver)
├── memento.py                   (undo/redo)
├── statistics.py                (stats tracking)
├── README.md                    (full documentation)
└── QUICK_START.md               (this file)
```

---

## 💡 Pro Tips

1. **Server Window**: Keep it open - it shows all activity logs
2. **Multiple Players**: Launch multiple human clients (each gets unique ID)
3. **Statistics**: Auto-saved after each game
4. **Undo**: Unlimited undo/redo in human mode
5. **Complexity**: Start with 3×3, then try larger sizes

---

## ✅ System Requirements

- **Python**: 3.10.x or higher
- **OS**: Windows, macOS, or Linux
- **Memory**: Minimal (< 100 MB)
- **Dependencies**: None (standard library only)

---

## 🎯 Common Tasks

### Play a Game:
1. Launch server → Launch human player
2. Click "New Game"
3. Click tiles to move
4. Solve the puzzle!

### Watch AI Solve:
1. Launch server → Launch computer player
2. Click "New Game & Solve"
3. Watch the magic! ✨

### View Statistics:
1. In human player window
2. Click "Show Report"
3. See all your game stats

### Try Different Sizes:
1. Select radio button (3×3, 4×4, etc.)
2. Board automatically resizes
3. Current game is abandoned

---

## 📞 Demo Checklist

For demonstrating to instructor:

- [ ] Server launches successfully
- [ ] Human client launches from server
- [ ] Can play and solve a puzzle
- [ ] Undo/Redo works
- [ ] Statistics report displays
- [ ] Unsolvable puzzle is detected
- [ ] Computer player launches
- [ ] AI solves a puzzle
- [ ] Size changes work
- [ ] Server log shows activities

---

## 🎓 Key Features to Highlight

1. **Single File Execution**: Only run server.py
2. **Design Patterns**: MVC, Singleton, Memento
3. **Solvability Detection**: Mathematical algorithm
4. **A* Algorithm**: Optimal pathfinding
5. **Full GUI**: No console I/O
6. **Statistics**: Persistent tracking
7. **Threading**: Concurrent clients

---

**Ready to start? Just run: `python server.py`** 🚀
