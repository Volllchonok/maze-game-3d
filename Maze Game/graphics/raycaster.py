import math
from typing import List, Dict

# Використовуємо Singleton
from design_patterns.singleton_settings import get_settings


class Raycaster:
    """Клас для рейкастингу з інтеграцією Singleton Pattern"""

    def __init__(self, player, maze):
        self.player = player
        self.maze = maze

        # Отримуємо налаштування через Singleton
        self.settings = get_settings()

        # Константи беруться з Singleton (динамічно змінюються!)
        self.half_fov = self.settings.FOV / 2
        self._update_settings()

    def _update_settings(self):
        """Оновлює налаштування з Singleton (може змінюватися динамічно)"""
        self.delta_angle = self.settings.FOV / self.settings.NUM_RAYS

    def cast_rays(self) -> List[Dict]:
        """Випускає промені з динамічними налаштуваннями"""
        # Оновлюємо налаштування на випадок їх зміни
        self._update_settings()

        rays = []
        start_angle = self.player.angle - self.half_fov

        # NUM_RAYS тепер може змінюватися динамічно!
        for i in range(self.settings.NUM_RAYS):
            angle = start_angle + i * self.delta_angle
            ray_data = self._cast_single_ray(angle)

            # Корекція fish-eye ефекту
            angle_diff = math.radians(angle - self.player.angle)
            corrected_distance = ray_data['distance'] * math.cos(angle_diff)

            rays.append({
                'distance': corrected_distance,
                'angle': angle,
                'wall_x': ray_data['wall_x'],
                'wall_y': ray_data['wall_y'],
                'texture_u': ray_data['texture_u'],
                'hit_vertical': ray_data['hit_vertical']
            })

        return rays

    def _cast_single_ray(self, angle: float) -> Dict:
        """Випускає один промінь з динамічними налаштуваннями"""
        angle_rad = math.radians(angle)
        dx = math.cos(angle_rad)
        dy = math.sin(angle_rad)

        step = 0.02  # Можна зробити це теж динамічним

        # MAX_DEPTH тепер з Singleton і може змінюватися!
        for i in range(int(self.settings.MAX_DEPTH / step)):
            distance = i * step
            x = self.player.x + dx * distance
            y = self.player.y + dy * distance

            if self.maze.is_wall(int(x), int(y)):
                # Визначаємо UV координату для текстури
                wall_x = x - int(x)
                wall_y = y - int(y)

                # Визначаємо тип стіни
                prev_x = self.player.x + dx * (distance - step)
                prev_y = self.player.y + dy * (distance - step)

                hit_vertical = int(prev_x) != int(x)

                if hit_vertical:
                    texture_u = wall_y
                else:
                    texture_u = wall_x

                return {
                    'distance': distance,
                    'wall_x': x,
                    'wall_y': y,
                    'texture_u': texture_u,
                    'hit_vertical': hit_vertical
                }

        return {
            'distance': self.settings.MAX_DEPTH,
            'wall_x': 0,
            'wall_y': 0,
            'texture_u': 0,
            'hit_vertical': False
        }

    def get_performance_info(self) -> Dict:
        """Повертає інформацію про поточні налаштування"""
        return {
            'num_rays': self.settings.NUM_RAYS,
            'max_depth': self.settings.MAX_DEPTH,
            'fov': self.settings.FOV
        }