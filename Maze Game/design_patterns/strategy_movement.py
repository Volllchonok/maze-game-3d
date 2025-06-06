import math
from abc import ABC, abstractmethod
from design_patterns.singleton_settings import get_settings


class MovementStrategy(ABC):
    """Абстрактна стратегія руху гравця"""

    @abstractmethod
    def calculate_movement(self, keys: dict, player, dt: float) -> tuple:
        """
        Обчислює рух гравця

        Args:
            keys: Словник натиснутих клавіш
            player: Об'єкт гравця
            dt: Час кадру

        Returns:
            tuple: (dx, dy, angle_change)
        """
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """Повертає назву стратегії"""
        pass


class EasyMovementStrategy(MovementStrategy):
    """
    Стратегія для легкого рівня
    Швидший рух, легше керування
    """

    def calculate_movement(self, keys: dict, player, dt: float) -> tuple:
        settings = get_settings()

        # Збільшена швидкість для легкого режиму
        speed = settings.PLAYER_SPEED * 1.3 * dt  # +30% швидкості
        turn_speed = settings.PLAYER_TURN_SPEED * 1.2 * dt  # +20% швидкості повороту

        return self._basic_movement_calculation(keys, player, speed, turn_speed)

    def _basic_movement_calculation(self, keys: dict, player, speed: float, turn_speed: float) -> tuple:
        """Базові обчислення руху"""
        dx = dy = 0
        angle_change = 0

        # Рух вперед/назад
        if keys.get('forward', False):
            angle_rad = math.radians(player.angle)
            dx += speed * math.cos(angle_rad)
            dy += speed * math.sin(angle_rad)
        if keys.get('backward', False):
            angle_rad = math.radians(player.angle)
            dx -= speed * math.cos(angle_rad)
            dy -= speed * math.sin(angle_rad)

        # Поворот
        if keys.get('turn_left', False):
            angle_change -= turn_speed
        if keys.get('turn_right', False):
            angle_change += turn_speed

        # Стрейф (бічний рух)
        if keys.get('strafe_left', False):
            angle_rad = math.radians(player.angle)
            dx -= speed * math.sin(angle_rad)
            dy += speed * math.cos(angle_rad)
        if keys.get('strafe_right', False):
            angle_rad = math.radians(player.angle)
            dx += speed * math.sin(angle_rad)
            dy -= speed * math.cos(angle_rad)

        return dx, dy, angle_change

    def get_strategy_name(self) -> str:
        return "Easy Movement (Fast)"


class NormalMovementStrategy(MovementStrategy):
    """
    Стандартна стратегія руху
    Збалансовані налаштування
    """

    def calculate_movement(self, keys: dict, player, dt: float) -> tuple:
        settings = get_settings()

        # Стандартні швидкості
        speed = settings.PLAYER_SPEED * dt
        turn_speed = settings.PLAYER_TURN_SPEED * dt

        return EasyMovementStrategy()._basic_movement_calculation(keys, player, speed, turn_speed)

    def get_strategy_name(self) -> str:
        return "Normal Movement"


class HardMovementStrategy(MovementStrategy):
    """
    Стратегія для важкого рівня
    Повільніший рух, важче керування
    """

    def calculate_movement(self, keys: dict, player, dt: float) -> tuple:
        settings = get_settings()

        # Зменшена швидкість для важкого режиму
        speed = settings.PLAYER_SPEED * 0.7 * dt  # -30% швидкості
        turn_speed = settings.PLAYER_TURN_SPEED * 0.8 * dt  # -20% швидкості повороту

        # Додаємо "інерцію" - рух не миттєвий
        dx, dy, angle_change = EasyMovementStrategy()._basic_movement_calculation(
            keys, player, speed, turn_speed
        )

        # Зменшуємо різкість рухів
        inertia_factor = 0.8
        dx *= inertia_factor
        dy *= inertia_factor
        angle_change *= inertia_factor

        return dx, dy, angle_change

    def get_strategy_name(self) -> str:
        return "Hard Movement (Slow + Inertia)"


class SmoothMovementStrategy(MovementStrategy):
    """
    Плавна стратегія руху з прискоренням
    Для досвідчених гравців
    """

    def __init__(self):
        self.velocity_x = 0
        self.velocity_y = 0
        self.angular_velocity = 0
        self.acceleration = 8.0
        self.friction = 0.85

    def calculate_movement(self, keys: dict, player, dt: float) -> tuple:
        settings = get_settings()

        max_speed = settings.PLAYER_SPEED * dt
        max_turn_speed = settings.PLAYER_TURN_SPEED * dt

        # Обчислюємо бажаний рух
        target_dx = target_dy = 0
        target_angular = 0

        if keys.get('forward', False):
            angle_rad = math.radians(player.angle)
            target_dx += max_speed * math.cos(angle_rad)
            target_dy += max_speed * math.sin(angle_rad)
        if keys.get('backward', False):
            angle_rad = math.radians(player.angle)
            target_dx -= max_speed * math.cos(angle_rad)
            target_dy -= max_speed * math.sin(angle_rad)

        if keys.get('turn_left', False):
            target_angular -= max_turn_speed
        if keys.get('turn_right', False):
            target_angular += max_turn_speed

        # Плавне прискорення до цільової швидкості
        self.velocity_x += (target_dx - self.velocity_x) * self.acceleration * dt
        self.velocity_y += (target_dy - self.velocity_y) * self.acceleration * dt
        self.angular_velocity += (target_angular - self.angular_velocity) * self.acceleration * dt

        # Тертя
        if not keys.get('forward', False) and not keys.get('backward', False):
            self.velocity_x *= self.friction
            self.velocity_y *= self.friction

        if not keys.get('turn_left', False) and not keys.get('turn_right', False):
            self.angular_velocity *= self.friction

        return self.velocity_x, self.velocity_y, self.angular_velocity

    def get_strategy_name(self) -> str:
        return "Smooth Movement (Acceleration)"


class MovementContext:
    """
    Контекст для Strategy Pattern
    Управляє поточною стратегією руху

    Використання:
    from design_patterns.strategy_movement import MovementContext, EasyMovementStrategy
    context = MovementContext(EasyMovementStrategy())
    dx, dy, angle = context.execute_movement(keys, player, dt)
    """

    def __init__(self, strategy: MovementStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: MovementStrategy):
        """Змінює поточну стратегію руху"""
        self._strategy = strategy

    def get_current_strategy(self) -> MovementStrategy:
        """Повертає поточну стратегію"""
        return self._strategy

    def execute_movement(self, keys: dict, player, dt: float) -> tuple:
        """Виконує рух використовуючи поточну стратегію"""
        return self._strategy.calculate_movement(keys, player, dt)

    def get_strategy_info(self) -> dict:
        """Повертає інформацію про поточну стратегію"""
        return {
            'name': self._strategy.get_strategy_name(),
            'type': type(self._strategy).__name__
        }


class MovementStrategyFactory:
    """
    Factory для створення стратегій руху

    Використання:
    from design_patterns.strategy_movement import MovementStrategyFactory
    from core.enums import Difficulty
    strategy = MovementStrategyFactory.create_for_difficulty(Difficulty.EASY)
    """

    @staticmethod
    def create_for_difficulty(difficulty) -> MovementStrategy:
        """Створює стратегію для заданої складності"""
        # Імпортуємо тут щоб уникнути циклічних імпортів
        from core.enums import Difficulty

        if difficulty == Difficulty.EASY:
            return EasyMovementStrategy()
        elif difficulty == Difficulty.HARD:
            return HardMovementStrategy()
        else:  # MEDIUM
            return NormalMovementStrategy()

    @staticmethod
    def create_smooth_strategy() -> MovementStrategy:
        """Створює плавну стратегію руху"""
        return SmoothMovementStrategy()

    @staticmethod
    def get_all_strategies() -> list:
        """Повертає всі доступні стратегії"""
        return [
            EasyMovementStrategy(),
            NormalMovementStrategy(),
            HardMovementStrategy(),
            SmoothMovementStrategy()
        ]