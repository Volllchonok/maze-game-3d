import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import math

# Додаємо шлях до проєкту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Імпортуємо pygame спершу
import pygame

from core.game import Game
from core.enums import Difficulty, GameState
from entities.player import Player
from entities.maze import Maze
from data.maze_data import MAZE_DATA, SPAWN_POINTS
from design_patterns.singleton_settings import GameSettings, get_settings
from design_patterns.factory_renderers import RendererFactory, RendererType, FastRenderer, QualityRenderer
from design_patterns.strategy_movement import (
    MovementContext, MovementStrategyFactory,
    EasyMovementStrategy, NormalMovementStrategy, HardMovementStrategy
)
from graphics.raycaster import Raycaster
from core.input_handler import InputHandler


class TestMazeGame(unittest.TestCase):

    def setUp(self):
        """Підготовка перед кожним тестом"""
        # Скидаємо singleton
        if hasattr(GameSettings, '_instance'):
            GameSettings._instance = None

        # Створюємо тестові об'єкти
        self.maze = Maze(Difficulty.EASY)
        self.player = Player(x=1.5, y=1.5)

    def test_01_player_initialization(self):
        """Тест ініціалізації гравця"""
        player = Player(x=5.0, y=10.0, angle=45.0)
        self.assertEqual(player.x, 5.0)
        self.assertEqual(player.y, 10.0)
        self.assertEqual(player.angle, 45.0)

    def test_02_player_position_methods(self):
        """Тест методів позиції гравця"""
        player = Player(x=1.0, y=1.0)

        # Тест get_position
        pos = player.get_position()
        self.assertEqual(pos, (1.0, 1.0))

        # Тест set_position
        player.set_position(2.5, 3.5)
        self.assertEqual(player.x, 2.5)
        self.assertEqual(player.y, 3.5)

    def test_03_player_angle_methods(self):
        """Тест методів кута гравця"""
        player = Player(x=1.0, y=1.0, angle=90.0)

        # Тест get_angle
        self.assertEqual(player.get_angle(), 90.0)

        # Тест set_angle з нормалізацією
        player.set_angle(450.0)  # 450 -> 90
        self.assertEqual(player.angle, 90.0)

        # Тест turn
        player.turn(45.0)
        self.assertEqual(player.angle, 135.0)

    def test_04_player_movement_methods(self):
        """Тест методів руху гравця"""
        player = Player(x=1.0, y=1.0, angle=0.0)  # Дивиться на схід

        # Тест move_forward
        initial_x = player.x
        player.move_forward(1.0)
        self.assertAlmostEqual(player.x, initial_x + 1.0, places=5)

        # Тест distance_to
        distance = player.distance_to(3.0, 1.0)
        self.assertAlmostEqual(distance, 1.0, places=5)

    def test_05_player_direction_vector(self):
        """Тест вектора напрямку гравця"""
        player = Player(x=0.0, y=0.0, angle=0.0)  # Дивиться на схід

        dx, dy = player.get_direction_vector()
        self.assertAlmostEqual(dx, 1.0, places=5)
        self.assertAlmostEqual(dy, 0.0, places=5)

        player.set_angle(90.0)  # Дивиться на північ
        dx, dy = player.get_direction_vector()
        self.assertAlmostEqual(dx, 0.0, places=5)
        self.assertAlmostEqual(dy, 1.0, places=5)

    def test_06_maze_initialization(self):
        """Тест ініціалізації лабіринту"""
        maze = Maze(Difficulty.EASY)

        # Перевіряємо розміри
        expected_data = MAZE_DATA[Difficulty.EASY]
        self.assertEqual(maze.width, len(expected_data[0]))
        self.assertEqual(maze.height, len(expected_data))

        # Перевіряємо spawn point
        expected_spawn = SPAWN_POINTS[Difficulty.EASY]
        self.assertEqual((maze.spawn_x, maze.spawn_y), expected_spawn)

    def test_07_maze_wall_detection(self):
        """Тест виявлення стін в лабіринті"""
        maze = Maze(Difficulty.EASY)

        # Тест стіни (перший елемент завжди стіна)
        self.assertTrue(maze.is_wall(0, 0))

        # Тест вільного простору
        self.assertFalse(maze.is_wall(1, 1))

        # Тест меж
        self.assertTrue(maze.is_wall(-1, 0))
        self.assertTrue(maze.is_wall(0, -1))
        self.assertTrue(maze.is_wall(maze.width, 0))
        self.assertTrue(maze.is_wall(0, maze.height))

    def test_08_maze_exit_detection(self):
        """Тест виявлення виходу в лабіринті"""
        maze = Maze(Difficulty.EASY)

        # Знаходимо вихід (9) в даних лабіринту
        exit_found = False
        for y, row in enumerate(MAZE_DATA[Difficulty.EASY]):
            for x, cell in enumerate(row):
                if cell == 9:
                    self.assertTrue(maze.is_exit(x, y))
                    exit_found = True
                    break
            if exit_found:
                break

        self.assertTrue(exit_found, "Вихід повинен бути знайдений в лабіринті")

        # Тест не-виходу
        self.assertFalse(maze.is_exit(0, 0))  # Стіна
        self.assertFalse(maze.is_exit(1, 1))  # Вільний простір

    def test_09_game_initialization(self):
        """Тест ініціалізації гри"""
        # Ініціалізуємо pygame для тестів
        pygame.init()

        # Мокаємо тільки display методи
        with patch('pygame.display.set_mode') as mock_set_mode, \
                patch('pygame.display.set_caption') as mock_caption:
            # Створюємо мок surface
            mock_surface = Mock()
            mock_surface.get_size.return_value = (800, 600)
            mock_set_mode.return_value = mock_surface

            game = Game()
            self.assertEqual(game.state, GameState.MENU)
            self.assertEqual(game.selected_option, 0)
            self.assertIsNone(game.current_difficulty)

    def test_10_game_level_start(self):
        """Тест запуску рівня"""
        pygame.init()

        with patch('pygame.display.set_mode') as mock_set_mode, \
                patch('pygame.display.set_caption') as mock_caption:
            mock_surface = Mock()
            mock_surface.get_size.return_value = (800, 600)
            mock_set_mode.return_value = mock_surface

            game = Game()
            game.start_level(Difficulty.EASY)

            self.assertEqual(game.state, GameState.PLAYING)
            self.assertEqual(game.current_difficulty, Difficulty.EASY)
            self.assertIsNotNone(game.maze)
            self.assertIsNotNone(game.player)
            self.assertIsNotNone(game.raycaster)

    def test_11_singleton_settings(self):
        """Тест паттерну Singleton для налаштувань"""
        # Скидаємо singleton
        if hasattr(GameSettings, '_instance'):
            GameSettings._instance = None

        settings1 = GameSettings()
        settings2 = GameSettings()
        settings3 = get_settings()

        # Всі посилання повинні вказувати на один об'єкт
        self.assertIs(settings1, settings2)
        self.assertIs(settings2, settings3)

    def test_12_singleton_settings_performance_adaptation(self):
        """Тест адаптації продуктивності в Singleton"""
        settings = get_settings()

        # Тест зниження продуктивності
        initial_rays = settings.NUM_RAYS
        result = settings.adapt_performance(25.0)  # Низький FPS
        self.assertEqual(result, "reduced")
        self.assertLess(settings.NUM_RAYS, initial_rays)

        # Тест підвищення продуктивності
        result = settings.adapt_performance(60.0)  # Високий FPS
        self.assertEqual(result, "increased")

        # Тест без змін
        result = settings.adapt_performance(45.0)  # Середній FPS
        self.assertEqual(result, "unchanged")

    def test_13_factory_renderer_creation(self):
        """Тест паттерну Factory для рендерерів"""
        # Створюємо реальний pygame surface для тестів
        pygame.init()
        screen = pygame.Surface((800, 600))

        factory = RendererFactory()

        # Тест створення швидкого рендерера
        fast_renderer = factory.create_renderer(RendererType.FAST, screen)
        self.assertIsInstance(fast_renderer, FastRenderer)

        # Тест створення якісного рендерера
        quality_renderer = factory.create_renderer(RendererType.QUALITY, screen)
        self.assertIsInstance(quality_renderer, QualityRenderer)

    def test_14_factory_adaptive_renderer(self):
        """Тест адаптивного створення рендерерів"""
        pygame.init()
        screen = pygame.Surface((800, 600))

        factory = RendererFactory()

        # Низький FPS -> швидкий рендерер
        renderer = factory.create_adaptive_renderer(screen, 30.0)
        self.assertIsInstance(renderer, FastRenderer)

        # Високий FPS -> якісний рендерер
        renderer = factory.create_adaptive_renderer(screen, 60.0)
        self.assertIsInstance(renderer, QualityRenderer)

    def test_15_movement_strategy_easy(self):
        """Тест стратегії легкого руху"""
        strategy = EasyMovementStrategy()
        player = Player(x=1.0, y=1.0, angle=0.0)
        keys = {'forward': True, 'turn_left': False, 'turn_right': False,
                'backward': False, 'strafe_left': False, 'strafe_right': False}

        dx, dy, angle_change = strategy.calculate_movement(keys, player, 0.016)  # ~60 FPS

        # Легка стратегія повинна давати більший рух
        self.assertGreater(abs(dx), 0)
        self.assertEqual(strategy.get_strategy_name(), "Easy Movement (Fast)")

    def test_16_movement_strategy_context(self):
        """Тест контексту для Strategy Pattern"""
        easy_strategy = EasyMovementStrategy()
        hard_strategy = HardMovementStrategy()

        context = MovementContext(easy_strategy)
        self.assertIs(context.get_current_strategy(), easy_strategy)

        # Зміна стратегії
        context.set_strategy(hard_strategy)
        self.assertIs(context.get_current_strategy(), hard_strategy)

        # Тест інформації про стратегію
        info = context.get_strategy_info()
        self.assertIn('name', info)
        self.assertIn('type', info)

    def test_17_movement_strategy_factory(self):
        """Тест Factory для стратегій руху"""
        # Тест створення для різних складностей
        easy_strategy = MovementStrategyFactory.create_for_difficulty(Difficulty.EASY)
        self.assertIsInstance(easy_strategy, EasyMovementStrategy)

        normal_strategy = MovementStrategyFactory.create_for_difficulty(Difficulty.MEDIUM)
        self.assertIsInstance(normal_strategy, NormalMovementStrategy)

        hard_strategy = MovementStrategyFactory.create_for_difficulty(Difficulty.HARD)
        self.assertIsInstance(hard_strategy, HardMovementStrategy)

    def test_18_raycaster_initialization(self):
        """Тест ініціалізації райкастера"""
        player = Player(x=1.5, y=1.5)
        maze = Maze(Difficulty.EASY)
        raycaster = Raycaster(player, maze)

        self.assertIs(raycaster.player, player)
        self.assertIs(raycaster.maze, maze)
        self.assertIsNotNone(raycaster.settings)

    def test_19_raycaster_cast_rays(self):
        """Тест випуску променів"""
        player = Player(x=1.5, y=1.5, angle=0.0)
        maze = Maze(Difficulty.EASY)
        raycaster = Raycaster(player, maze)

        rays = raycaster.cast_rays()

        # Перевіряємо що промені повернулися
        self.assertIsInstance(rays, list)
        self.assertGreater(len(rays), 0)

        # Перевіряємо структуру променя
        if rays:
            ray = rays[0]
            required_keys = ['distance', 'angle', 'wall_x', 'wall_y', 'texture_u', 'hit_vertical']
            for key in required_keys:
                self.assertIn(key, ray)

    def test_20_input_handler(self):
        """Тест обробника введення"""
        # Створюємо словник з правильними pygame константами
        mock_key_state = {
            pygame.K_w: True,
            pygame.K_a: False,
            pygame.K_s: False,
            pygame.K_d: True,
            pygame.K_LEFT: False,
            pygame.K_RIGHT: True,
            pygame.K_UP: False,
            pygame.K_DOWN: False,
            pygame.K_q: False,
            pygame.K_e: False
        }

        with patch('pygame.key.get_pressed', return_value=mock_key_state):
            keys = InputHandler.get_movement_keys()

            self.assertTrue(keys['forward'])  # W натиснуто
            self.assertFalse(keys['strafe_left'])  # A не натиснуто
            self.assertTrue(keys['strafe_right'])  # D натиснуто
            self.assertTrue(keys['turn_right'])  # RIGHT натиснуто
            self.assertFalse(keys['backward'])  # S не натиснуто

    def tearDown(self):
        """Очищення після кожного тесту"""
        # Скидаємо singleton settings
        if hasattr(GameSettings, '_instance'):
            GameSettings._instance = None


# Додаткові хелпери та налаштування
def setUpModule():
    """Налаштування модуля перед запуском тестів"""
    # Ініціалізуємо pygame один раз для всіх тестів
    pygame.init()
    # Встановлюємо режим без виводу (headless)
    import os
    os.environ['SDL_VIDEODRIVER'] = 'dummy'


def tearDownModule():
    """Очищення після всіх тестів"""
    pygame.quit()


if __name__ == '__main__':

    unittest.main(verbosity=2, buffer=True)