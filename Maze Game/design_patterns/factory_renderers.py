"""
Factory Pattern - Створення рендерерів
Файл: design_patterns/factory_renderers.py

Створює різні рендерери залежно від продуктивності
"""

import pygame
import math
from abc import ABC, abstractmethod
from enum import Enum
from design_patterns.singleton_settings import get_settings


class RendererType(Enum):
    """Типи рендерерів"""
    FAST = "fast"
    QUALITY = "quality"


class BaseRenderer(ABC):
    """Базовий клас для всіх рендерерів"""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.settings = get_settings()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

    @abstractmethod
    def render_3d_view(self, rays, player_angle=0):
        """Рендерить 3D вигляд"""
        pass

    @abstractmethod
    def get_renderer_info(self) -> dict:
        """Повертає інформацію про рендерер"""
        pass


class FastRenderer(BaseRenderer):
    """
    Швидкий рендерер для слабких ПК
    Оптимізації: товщі смужки, групування кольорів, простіше освітлення
    """

    def render_3d_view(self, rays, player_angle=0):
        """Швидкий рендеринг"""
        # Небо - простий колір
        pygame.draw.rect(self.screen, self.settings.CEILING_COLOR,
                         (0, 0, self.settings.WIDTH, self.settings.HEIGHT // 2))

        # Підлога
        pygame.draw.rect(self.screen, self.settings.FLOOR_COLOR,
                         (0, self.settings.HEIGHT // 2, self.settings.WIDTH, self.settings.HEIGHT // 2))

        # Стіни - ОПТИМІЗОВАНО
        if not rays:
            return

        strip_width = self.settings.WIDTH / len(rays)

        # Групуємо за кольором для швидшого рендерингу
        color_groups = {}

        for i, ray in enumerate(rays):
            distance = ray.get('distance', self.settings.MAX_DEPTH)
            if distance <= 0:
                continue

            wall_height = min(self.settings.HEIGHT, max(1, int(self.settings.HEIGHT / distance)))
            wall_top = (self.settings.HEIGHT - wall_height) // 2

            # Простіше освітлення
            brightness = max(30, 255 - int(distance * 25))
            color = (brightness, brightness // 2, brightness // 4)

            if color not in color_groups:
                color_groups[color] = []

            rect = pygame.Rect(int(i * strip_width), wall_top,
                               max(2, int(strip_width)), wall_height)
            color_groups[color].append(rect)

        # Малюємо групами
        for color, rects in color_groups.items():
            for rect in rects:
                pygame.draw.rect(self.screen, color, rect)

    def render_compass(self, player_angle):
        """Спрощений компас"""
        center = (self.settings.WIDTH - 60, 60)
        radius = 25

        pygame.draw.circle(self.screen, self.settings.DARK_GRAY, center, radius)
        pygame.draw.circle(self.screen, self.settings.WHITE, center, radius, 2)

        # Тільки стрілка
        angle_rad = math.radians(player_angle)
        arrow_end_x = center[0] + int((radius - 8) * math.sin(angle_rad))
        arrow_end_y = center[1] - int((radius - 8) * math.cos(angle_rad))

        pygame.draw.line(self.screen, self.settings.RED, center, (arrow_end_x, arrow_end_y), 3)

    def get_renderer_info(self) -> dict:
        return {
            'type': 'FastRenderer',
            'optimization': 'high',
            'quality': 'low'
        }


class QualityRenderer(BaseRenderer):
    """
    Якісний рендерер для потужних ПК
    Покращення: градієнт неба, варіація кольорів, детальний компас
    """

    def render_3d_view(self, rays, player_angle=0):
        """Якісний рендеринг"""
        # Градієнт неба
        for y in range(self.settings.HEIGHT // 2):
            progress = y / (self.settings.HEIGHT // 2)
            blue = int(80 + progress * 40)
            color = (30, 50, blue)
            pygame.draw.line(self.screen, color, (0, y), (self.settings.WIDTH, y))

        # Підлога з легким градієнтом
        base_floor = self.settings.FLOOR_COLOR
        for y in range(self.settings.HEIGHT // 2):
            shade = int(y * 0.1)
            color = tuple(max(0, min(255, c + shade)) for c in base_floor)
            pygame.draw.line(self.screen, color,
                             (0, self.settings.HEIGHT // 2 + y),
                             (self.settings.WIDTH, self.settings.HEIGHT // 2 + y))

        # Детальні стіни
        if not rays:
            return

        strip_width = self.settings.WIDTH / len(rays)

        for i, ray in enumerate(rays):
            distance = ray.get('distance', self.settings.MAX_DEPTH)
            if distance <= 0:
                continue

            wall_height = min(self.settings.HEIGHT, max(1, int(self.settings.HEIGHT / distance)))
            wall_top = (self.settings.HEIGHT - wall_height) // 2

            # Складніше освітлення з варіацією
            brightness = max(50, 255 - int(distance * 12))
            wall_x = ray.get('wall_x', 0)
            wall_y = ray.get('wall_y', 0)

            # Варіація кольору
            variation = int((wall_x + wall_y) * 30) % 50
            color = (
                min(255, brightness + variation),
                min(255, brightness // 2 + variation // 2),
                min(255, brightness // 4 + variation // 4)
            )

            rect = pygame.Rect(int(i * strip_width), wall_top,
                               max(1, int(strip_width)), wall_height)
            pygame.draw.rect(self.screen, color, rect)

    def render_compass(self, player_angle):
        """Детальний компас"""
        center = (self.settings.WIDTH - 80, 80)
        radius = 40

        pygame.draw.circle(self.screen, self.settings.DARK_GRAY, center, radius)
        pygame.draw.circle(self.screen, self.settings.WHITE, center, radius, 2)

        # Напрямки
        directions = [("Пн", 0), ("Сх", 90), ("Пд", 180), ("Зх", 270)]

        for text, angle in directions:
            angle_rad = math.radians(angle)
            text_x = center[0] + int((radius - 15) * math.sin(angle_rad))
            text_y = center[1] - int((radius - 15) * math.cos(angle_rad))

            text_surface = self.small_font.render(text, True, self.settings.WHITE)
            text_rect = text_surface.get_rect(center=(text_x, text_y))
            self.screen.blit(text_surface, text_rect)

        # Стрілка з деталями
        angle_rad = math.radians(player_angle)
        arrow_end_x = center[0] + int((radius - 10) * math.sin(angle_rad))
        arrow_end_y = center[1] - int((radius - 10) * math.cos(angle_rad))

        pygame.draw.line(self.screen, self.settings.RED, center, (arrow_end_x, arrow_end_y), 3)
        pygame.draw.circle(self.screen, self.settings.RED, (arrow_end_x, arrow_end_y), 3)

    def get_renderer_info(self) -> dict:
        return {
            'type': 'QualityRenderer',
            'optimization': 'low',
            'quality': 'high'
        }


class RendererFactory:
    """
    Factory Method для створення рендерерів

    Використання:
    from design_patterns.factory_renderers import RendererFactory
    renderer = RendererFactory.create_adaptive_renderer(screen, fps)
    """

    @staticmethod
    def create_renderer(renderer_type: RendererType, screen: pygame.Surface) -> BaseRenderer:
        """Створює рендерер заданого типу"""
        if renderer_type == RendererType.FAST:
            return FastRenderer(screen)
        elif renderer_type == RendererType.QUALITY:
            return QualityRenderer(screen)
        else:
            raise ValueError(f"Невідомий тип рендерера: {renderer_type}")

    @staticmethod
    def create_adaptive_renderer(screen: pygame.Surface, current_fps: float) -> BaseRenderer:
        """Створює рендерер адаптивно під FPS"""
        if current_fps < 35:
            return FastRenderer(screen)
        else:
            return QualityRenderer(screen)

    @staticmethod
    def create_optimal_renderer(screen: pygame.Surface) -> BaseRenderer:
        """Створює збалансований рендерер"""
        return QualityRenderer(screen)

    @staticmethod
    def get_available_types() -> list:
        """Повертає доступні типи рендерерів"""
        return list(RendererType)