import pygame
from typing import Dict


class InputHandler:
    """Обробник введення"""

    @staticmethod
    def get_movement_keys() -> Dict[str, bool]:
        """Повертає стан клавіш руху"""
        keys = pygame.key.get_pressed()
        return {
            'forward': keys[pygame.K_w] or keys[pygame.K_UP],
            'backward': keys[pygame.K_s] or keys[pygame.K_DOWN],
            'strafe_left': keys[pygame.K_a],
            'strafe_right': keys[pygame.K_d],
            'turn_left': keys[pygame.K_LEFT] or keys[pygame.K_q],
            'turn_right': keys[pygame.K_RIGHT] or keys[pygame.K_e]
        }