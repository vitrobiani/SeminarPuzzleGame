"""
Statistics Module
=================
This module tracks game statistics for generating reports.

Classes:
    GameStats: Stores statistics for a specific puzzle size
    StatsTracker: Manages statistics for all puzzle sizes
"""

from typing import Dict
import json
import os


class GameStats:
    """
    Stores statistics for games of a specific size.

    Tracks number of games played, solved, unsolvable, abandoned,
    average time, and average moves.

    Attributes:
        size (int): Puzzle dimension
        total_games (int): Total games played
        unsolvable_games (int): Games that were unsolvable
        abandoned_games (int): Games started but not finished
        solved_games (int): Games successfully solved
        total_time (float): Cumulative time spent solving
        total_moves (int): Cumulative moves made in solved games
        games_list (list): List of individual game results (dicts with 'time' and 'moves')
    """

    def __init__(self, size: int):
        """
        Initialize game statistics for a puzzle size.

        Args:
            size: Puzzle dimension
        """
        self.size = size
        self.total_games = 0
        self.unsolvable_games = 0
        self.abandoned_games = 0
        self.solved_games = 0
        self.total_time = 0.0
        self.total_moves = 0
        self.games_list = []  # Store individual game results
    
    def add_unsolvable(self):
        """Record an unsolvable game."""
        self.total_games += 1
        self.unsolvable_games += 1
    
    def add_abandoned(self):
        """Record an abandoned game."""
        self.total_games += 1
        self.abandoned_games += 1
    
    def add_solved(self, time_seconds: float, moves: int):
        """
        Record a solved game.

        Args:
            time_seconds: Time taken to solve
            moves: Number of moves made
        """
        self.total_games += 1
        self.solved_games += 1
        self.total_time += time_seconds
        self.total_moves += moves
        self.games_list.append({
            'time': time_seconds,
            'moves': moves
        })
    
    def get_average_time(self) -> float:
        """
        Get average solving time.
        
        Returns:
            float: Average time in seconds, or 0 if no games solved
        """
        if self.solved_games == 0:
            return 0.0
        return self.total_time / self.solved_games
    
    def get_average_moves(self) -> float:
        """
        Get average number of moves.
        
        Returns:
            float: Average moves, or 0 if no games solved
        """
        if self.solved_games == 0:
            return 0.0
        return self.total_moves / self.solved_games
    
    def to_dict(self) -> Dict:
        """
        Convert statistics to dictionary.
        
        Returns:
            Dict: Statistics as dictionary
        """
        return {
            'size': self.size,
            'total_games': self.total_games,
            'unsolvable_games': self.unsolvable_games,
            'abandoned_games': self.abandoned_games,
            'solved_games': self.solved_games,
            'average_time': round(self.get_average_time(), 2),
            'average_moves': round(self.get_average_moves(), 2)
        }
    
    def from_dict(self, data: Dict):
        """
        Load statistics from dictionary.

        Args:
            data: Dictionary containing statistics
        """
        self.total_games = data.get('total_games', 0)
        self.unsolvable_games = data.get('unsolvable_games', 0)
        self.abandoned_games = data.get('abandoned_games', 0)
        self.solved_games = data.get('solved_games', 0)
        self.total_time = data.get('total_time', 0.0)
        self.total_moves = data.get('total_moves', 0)
        self.games_list = data.get('games_list', [])


class StatsTracker:
    """
    Manages statistics for all puzzle sizes.
    
    Tracks statistics separately for each puzzle dimension (3x3, 4x4, etc.)
    and provides methods to save/load statistics.
    
    Attributes:
        client_id (int): ID of the client these stats belong to
        stats (Dict[int, GameStats]): Statistics for each puzzle size
    """
    
    def __init__(self, client_id: int):
        """
        Initialize statistics tracker.
        
        Args:
            client_id: ID of the client
        """
        self.client_id = client_id
        self.stats: Dict[int, GameStats] = {}
        
        # Initialize stats for all supported sizes
        for size in [3, 4, 5, 6, 7]:
            self.stats[size] = GameStats(size)
    
    def get_stats(self, size: int) -> GameStats:
        """
        Get statistics for a specific puzzle size.
        
        Args:
            size: Puzzle dimension
            
        Returns:
            GameStats: Statistics object
        """
        if size not in self.stats:
            self.stats[size] = GameStats(size)
        return self.stats[size]
    
    def record_unsolvable(self, size: int):
        """
        Record an unsolvable game.
        
        Args:
            size: Puzzle dimension
        """
        self.get_stats(size).add_unsolvable()
    
    def record_abandoned(self, size: int):
        """
        Record an abandoned game.
        
        Args:
            size: Puzzle dimension
        """
        self.get_stats(size).add_abandoned()
    
    def record_solved(self, size: int, time_seconds: float, moves: int):
        """
        Record a solved game.
        
        Args:
            size: Puzzle dimension
            time_seconds: Time taken to solve
            moves: Number of moves made
        """
        self.get_stats(size).add_solved(time_seconds, moves)
    
    def get_all_stats(self) -> Dict[int, Dict]:
        """
        Get all statistics as dictionary.
        
        Returns:
            Dict[int, Dict]: Statistics for all sizes
        """
        return {size: stats.to_dict() for size, stats in self.stats.items()}
    
    def save_to_file(self, filename: str):
        """
        Save statistics to JSON file.

        Args:
            filename: Path to save file
        """
        data = {
            'client_id': self.client_id,
            'stats': {}
        }

        for size, stats in self.stats.items():
            data['stats'][size] = {
                'total_games': stats.total_games,
                'unsolvable_games': stats.unsolvable_games,
                'abandoned_games': stats.abandoned_games,
                'solved_games': stats.solved_games,
                'total_time': stats.total_time,
                'total_moves': stats.total_moves,
                'games_list': stats.games_list
            }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_from_file(self, filename: str):
        """
        Load statistics from JSON file.
        
        Args:
            filename: Path to load file
        """
        if not os.path.exists(filename):
            return
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.client_id = data.get('client_id', self.client_id)
            
            stats_data = data.get('stats', {})
            for size_str, stats_dict in stats_data.items():
                size = int(size_str)
                if size not in self.stats:
                    self.stats[size] = GameStats(size)
                self.stats[size].from_dict(stats_dict)
        except Exception as e:
            print(f"Error loading statistics: {e}")
    
    def format_report(self) -> str:
        """
        Format statistics as a readable report.
        
        Returns:
            str: Formatted report text
        """
        report_lines = [
            f"=== Statistics Report for Client {self.client_id} ===\n"
        ]
        
        for size in sorted(self.stats.keys()):
            stats = self.stats[size]
            if stats.total_games == 0:
                continue
            
            report_lines.append(f"\n{size}x{size} Puzzle:")
            report_lines.append(f"  Total Games: {stats.total_games}")
            report_lines.append(f"  Unsolvable: {stats.unsolvable_games}")
            report_lines.append(f"  Abandoned: {stats.abandoned_games}")
            report_lines.append(f"  Solved: {stats.solved_games}")
            
            if stats.solved_games > 0:
                report_lines.append(f"  Average Time: {stats.get_average_time():.2f} seconds")
                report_lines.append(f"  Average Moves: {stats.get_average_moves():.2f}")
        
        return "\n".join(report_lines)
