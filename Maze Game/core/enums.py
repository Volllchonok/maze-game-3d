from enum import Enum


class Difficulty(Enum):
    """Рівні складності"""
    EASY = "легкий"
    MEDIUM = "середній"
    HARD = "важкий"


class GameState(Enum):
    """Стани гри"""
    MENU = "меню"
    PLAYING = "гра"
    PAUSED = "пауза"
    COMPLETED = "завершено"