import math
from typing import Dict


class Player:
    """Клас гравця"""

    def __init__(self, x: float, y: float, angle: float = 0):
        """
        Ініціалізує гравця

        Args:
            x: Початкова X координата
            y: Початкова Y координата
            angle: Початковий кут повороту в градусах
        """
        self.x = x
        self.y = y
        self.angle = angle  # в градусах

    def update(self, keys: Dict[str, bool], maze, dt: float) -> bool:
        """
        Оновлює позицію гравця (стара версія для сумісності)

        Args:
            keys: Словник натиснутих клавіш
            maze: Об'єкт лабіринту
            dt: Час кадру

        Returns:
            bool: True якщо рівень завершено (досягнуто виходу)
        """
        # Імпортуємо налаштування
        try:
            from design_patterns.singleton_settings import get_settings
            settings = get_settings()
            player_speed = settings.PLAYER_SPEED
            turn_speed = settings.PLAYER_TURN_SPEED
            radius = settings.PLAYER_RADIUS
        except ImportError:

            player_speed = 3.0
            turn_speed = 120.0
            radius = 0.2

        # Поворот
        if keys.get('turn_left', False):
            self.angle -= turn_speed * dt
        if keys.get('turn_right', False):
            self.angle += turn_speed * dt

        self.angle = self.angle % 360

        # Рух
        speed = player_speed * dt
        angle_rad = math.radians(self.angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        dx = dy = 0

        if keys.get('forward', False):
            dx += speed * cos_a
            dy += speed * sin_a
        if keys.get('backward', False):
            dx -= speed * cos_a
            dy -= speed * sin_a
        if keys.get('strafe_left', False):
            dx -= speed * sin_a
            dy += speed * cos_a
        if keys.get('strafe_right', False):
            dx += speed * sin_a
            dy -= speed * cos_a

        # Перевірка колізій
        new_x = self.x + dx
        new_y = self.y + dy

        if self._can_move_to(new_x, self.y, maze, radius):
            self.x = new_x
        if self._can_move_to(self.x, new_y, maze, radius):
            self.y = new_y

        # Перевірка виходу
        if maze.is_exit(int(self.x), int(self.y)):
            return True  # Рівень пройдено

        return False

    def _can_move_to(self, x: float, y: float, maze, radius: float = 0.2) -> bool:
        """
        Перевіряє чи можна рухатися в позицію

        Args:
            x: X координата
            y: Y координата
            maze: Об'єкт лабіринту
            radius: Радіус гравця

        Returns:
            bool: True якщо рух можливий
        """
        # Перевіряємо кути хітбоксу гравця
        corners = [
            (x - radius, y - radius),
            (x + radius, y - radius),
            (x - radius, y + radius),
            (x + radius, y + radius)
        ]

        for corner_x, corner_y in corners:
            if maze.is_wall(int(corner_x), int(corner_y)):
                return False

        return True

    def get_position(self) -> tuple:
        """Повертає поточну позицію гравця"""
        return (self.x, self.y)

    def get_angle(self) -> float:
        """Повертає поточний кут гравця в градусах"""
        return self.angle

    def set_position(self, x: float, y: float):
        """Встановлює позицію гравця"""
        self.x = x
        self.y = y

    def set_angle(self, angle: float):
        """Встановлює кут гравця"""
        self.angle = angle % 360

    def move_forward(self, distance: float):
        """Рухає гравця вперед на задану відстань"""
        angle_rad = math.radians(self.angle)
        self.x += distance * math.cos(angle_rad)
        self.y += distance * math.sin(angle_rad)

    def turn(self, angle_change: float):
        """Повертає гравця на заданий кут"""
        self.angle = (self.angle + angle_change) % 360

    def get_direction_vector(self) -> tuple:
        """Повертає вектор напрямку гравця"""
        angle_rad = math.radians(self.angle)
        return (math.cos(angle_rad), math.sin(angle_rad))

    def distance_to(self, x: float, y: float) -> float:
        """Обчислює відстань до заданої точки"""
        dx = x - self.x
        dy = y - self.y
        return math.sqrt(dx * dx + dy * dy)

    def __str__(self) -> str:
        """Рядкове представлення гравця"""
        return f"Player(x={self.x:.2f}, y={self.y:.2f}, angle={self.angle:.1f}°)"

    def __repr__(self) -> str:
        """Детальне представлення гравця"""
        return self.__str__()