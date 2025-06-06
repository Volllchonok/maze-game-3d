import threading
from typing import Dict, Any, Optional


class GameSettings:
    """
    Singleton для централізованого управління налаштуваннями

    Використання:
    from design_patterns.singleton_settings import GameSettings
    settings = GameSettings()
    """

    _instance: Optional['GameSettings'] = None
    _lock = threading.Lock()

    def __new__(cls) -> 'GameSettings':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return

        # Замінюють ваші константи з config/settings.py
        self.WIDTH = 800
        self.HEIGHT = 600
        self.FPS = 60

        # Кольори
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (100, 100, 100)
        self.DARK_GRAY = (64, 64, 64)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.YELLOW = (255, 255, 0)
        self.BLUE = (0, 100, 255)

        # Кольори світу
        self.FLOOR_COLOR = (40, 40, 40)
        self.CEILING_COLOR = (80, 80, 120)
        self.WALL_COLOR = (150, 100, 50)
        self.EXIT_COLOR = (0, 255, 0)

        # Рейкастинг - АДАПТИВНІ
        self.FOV = 60
        self.NUM_RAYS = 120  # Змінюється автоматично
        self.MAX_DEPTH = 15  # Змінюється автоматично

        # Гравець
        self.PLAYER_SPEED = 3.0
        self.PLAYER_TURN_SPEED = 120.0
        self.PLAYER_RADIUS = 0.2

        self._observers = []
        self._initialized = True

    def adapt_performance(self, fps: float) -> str:
        """РЕАЛЬНА адаптація під FPS"""
        if fps < 30:
            # Знижуємо якість
            self.NUM_RAYS = 60
            self.MAX_DEPTH = 8
            return "reduced"
        elif fps > 55:
            # Підвищуємо якість
            self.NUM_RAYS = 150
            self.MAX_DEPTH = 20
            return "increased"
        return "unchanged"

    def get_performance_settings(self) -> Dict[str, int]:
        """Повертає поточні налаштування продуктивності"""
        return {
            'num_rays': self.NUM_RAYS,
            'max_depth': self.MAX_DEPTH,
            'fps': self.FPS
        }

    def add_observer(self, observer):
        """Додає спостерігач за змінами"""
        self._observers.append(observer)

    def notify_observers(self, event: str, data: Dict[str, Any]):
        """Сповіщає спостерігачів"""
        for observer in self._observers:
            if hasattr(observer, 'on_settings_changed'):
                observer.on_settings_changed(event, data)


# Глобальна функція для легкого доступу
def get_settings() -> GameSettings:
    """Повертає екземпляр налаштувань"""
    return GameSettings()