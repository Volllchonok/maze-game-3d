
from core.enums import Difficulty
from data.maze_data import MAZE_DATA, SPAWN_POINTS


class Maze:
    """Клас лабіринту"""

    def __init__(self, difficulty: Difficulty):
        self.difficulty = difficulty
        self.maze_data = MAZE_DATA[difficulty]
        self.width = len(self.maze_data[0])
        self.height = len(self.maze_data)
        self.spawn_x, self.spawn_y = SPAWN_POINTS[difficulty]

    def is_wall(self, x: int, y: int) -> bool:
        """Перевіряє чи є стіна в заданій позиції"""
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return True
        return self.maze_data[y][x] == 1

    def is_exit(self, x: int, y: int) -> bool:
        """Перевіряє чи є вихід в заданій позиції"""
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return False
        return self.maze_data[y][x] == 9