import pygame
import sys
from core.enums import Difficulty, GameState
from core.input_handler import InputHandler
from entities.maze import Maze
from entities.player import Player
from graphics.raycaster import Raycaster

try:
    from design_patterns.singleton_settings import get_settings
    from design_patterns.factory_renderers import RendererFactory, RendererType
    from design_patterns.strategy_movement import MovementContext, MovementStrategyFactory

    PATTERNS_AVAILABLE = True
except ImportError:
    print("⚠️ Design Patterns не знайдені, використовуємо стандартний режим")
    PATTERNS_AVAILABLE = False


class Game:
    """Головний клас гри"""

    def __init__(self):
        pygame.init()

        if PATTERNS_AVAILABLE:
            # Використовуємо Singleton для налаштувань
            self.settings = get_settings()
            WIDTH = self.settings.WIDTH
            HEIGHT = self.settings.HEIGHT
            FPS = self.settings.FPS
        else:
            # Fallback константи
            WIDTH = 800
            HEIGHT = 600
            FPS = 60
            self.settings = None

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("3D Лабіринт")
        self.clock = pygame.time.Clock()

        # Стан гри
        self.state = GameState.MENU
        self.selected_option = 0
        self.current_difficulty = None

        # Ігрові об'єкти
        self.maze = None
        self.player = None
        self.raycaster = None

        # Рендерер та патерни
        if PATTERNS_AVAILABLE:
            self.renderer_factory = RendererFactory()
            self.renderer = self.renderer_factory.create_optimal_renderer(self.screen)
            self.movement_context = MovementContext(
                MovementStrategyFactory.create_for_difficulty(Difficulty.MEDIUM)
            )
        else:
            self.renderer = SimpleRenderer(self.screen)
            self.movement_context = None

        self.input_handler = InputHandler()
        self.running = True

        # Константи для fallback режиму
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.FPS = FPS

    def start_level(self, difficulty: Difficulty):
        """Запускає рівень"""
        self.current_difficulty = difficulty
        self.maze = Maze(difficulty)
        self.player = Player(self.maze.spawn_x, self.maze.spawn_y)
        self.raycaster = Raycaster(self.player, self.maze)

        # Налаштовуємо Strategy для руху якщо доступно
        if PATTERNS_AVAILABLE and self.movement_context:
            movement_strategy = MovementStrategyFactory.create_for_difficulty(difficulty)
            self.movement_context.set_strategy(movement_strategy)

        self.state = GameState.PLAYING

    def handle_events(self):
        """Обробка подій"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    self._handle_menu_input(event.key)
                elif self.state == GameState.PLAYING:
                    self._handle_game_input(event.key)
                elif self.state == GameState.PAUSED:
                    self._handle_pause_input(event.key)
                elif self.state == GameState.COMPLETED:
                    self._handle_completion_input(event.key)

    def _handle_menu_input(self, key):
        """Обробка введення в меню"""
        if key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % 4
        elif key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % 4
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            if self.selected_option == 0:
                self.start_level(Difficulty.EASY)
            elif self.selected_option == 1:
                self.start_level(Difficulty.MEDIUM)
            elif self.selected_option == 2:
                self.start_level(Difficulty.HARD)
            elif self.selected_option == 3:
                self.running = False

    def _handle_game_input(self, key):
        """Обробка введення під час гри"""
        if key == pygame.K_ESCAPE:
            self.state = GameState.MENU
        elif key == pygame.K_SPACE:
            self.state = GameState.PAUSED

    def _handle_pause_input(self, key):
        """Обробка введення в паузі"""
        if key == pygame.K_SPACE:
            self.state = GameState.PLAYING
        elif key == pygame.K_ESCAPE:
            self.state = GameState.MENU

    def _handle_completion_input(self, key):
        """Обробка введення на екрані завершення"""
        if key == pygame.K_SPACE or key == pygame.K_RETURN:
            self.state = GameState.MENU

    def update(self, dt: float):
        """Оновлення логіки гри"""
        if self.state == GameState.PLAYING:
            keys = self.input_handler.get_movement_keys()

            if PATTERNS_AVAILABLE and self.movement_context:
                # Використовуємо Strategy Pattern для руху
                dx, dy, angle_change = self.movement_context.execute_movement(keys, self.player, dt)

                # Застосовуємо рух
                new_x = self.player.x + dx
                new_y = self.player.y + dy

                if self.player._can_move_to(new_x, self.player.y, self.maze):
                    self.player.x = new_x
                if self.player._can_move_to(self.player.x, new_y, self.maze):
                    self.player.y = new_y

                self.player.angle = (self.player.angle + angle_change) % 360
            else:
                # Fallback - використовуємо стандартний метод Player
                level_completed = self.player.update(keys, self.maze, dt)
                if level_completed:
                    self.state = GameState.COMPLETED
                    return

            # Перевірка виходу
            if self.maze.is_exit(int(self.player.x), int(self.player.y)):
                self.state = GameState.COMPLETED

    def render(self):
        """Рендеринг гри"""
        if self.state == GameState.MENU:
            self.render_menu()

        elif self.state == GameState.PLAYING:
            # Адаптивний рендеринг якщо патерни доступні
            if PATTERNS_AVAILABLE and hasattr(self, 'renderer_factory'):
                current_fps = self.clock.get_fps()
                perf_change = self.settings.adapt_performance(current_fps)

                # Змінюємо рендерер якщо потрібно
                if perf_change == "reduced":
                    self.renderer = self.renderer_factory.create_renderer(RendererType.FAST, self.screen)
                elif perf_change == "increased":
                    self.renderer = self.renderer_factory.create_renderer(RendererType.QUALITY, self.screen)

            # Рендеримо 3D
            rays = self.raycaster.cast_rays()
            self.renderer.render_3d_view(rays, self.player.angle)

            if hasattr(self.renderer, 'render_compass'):
                self.renderer.render_compass(self.player.angle)

            # Інформація про патерни
            if PATTERNS_AVAILABLE:
                self._render_pattern_info()

        elif self.state == GameState.PAUSED:
            rays = self.raycaster.cast_rays()
            self.renderer.render_3d_view(rays, self.player.angle)
            if hasattr(self.renderer, 'render_compass'):
                self.renderer.render_compass(self.player.angle)
            self.render_pause_menu()

        elif self.state == GameState.COMPLETED:
            self.render_completion_screen()

        pygame.display.flip()

    def _render_pattern_info(self):
        """Рендерить інформацію про патерни"""
        if not PATTERNS_AVAILABLE:
            return

        current_fps = self.clock.get_fps()
        font = pygame.font.Font(None, 24)

        info_lines = [
            f"FPS: {current_fps:.1f}",
            f"Rays: {self.settings.NUM_RAYS}",
            f"Renderer: {self.renderer.get_renderer_info()['type']}",
        ]

        if self.movement_context:
            strategy_info = self.movement_context.get_strategy_info()
            info_lines.append(f"Movement: {strategy_info['name']}")

        y_offset = 10
        for line in info_lines:
            surface = font.render(line, True, (255, 255, 255))
            self.screen.blit(surface, (10, y_offset))
            y_offset += 20

    def render_menu(self):
        """Рендеринг головного меню"""
        # Кольори
        BLACK = (0, 0, 0) if not self.settings else self.settings.BLACK
        WHITE = (255, 255, 255) if not self.settings else self.settings.WHITE
        YELLOW = (255, 255, 0) if not self.settings else self.settings.YELLOW
        GRAY = (128, 128, 128) if not self.settings else self.settings.GRAY

        self.screen.fill(BLACK)

        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)

        # Заголовок
        title_text = "3D ЛАБІРИНТ"
        if PATTERNS_AVAILABLE:
            title_text += " (Design Patterns)"

        title = font.render(title_text, True, WHITE)
        title_rect = title.get_rect(center=(self.WIDTH // 2, 150))
        self.screen.blit(title, title_rect)

        # Опції меню
        options = ["Легкий", "Середній", "Важкий", "Вихід"]
        colors = [YELLOW if i == self.selected_option else WHITE for i in range(len(options))]

        for i, (option, color) in enumerate(zip(options, colors)):
            text = font.render(option, True, color)
            text_rect = text.get_rect(center=(self.WIDTH // 2, 250 + i * 60))
            self.screen.blit(text, text_rect)

        # Інформація про рівні
        if PATTERNS_AVAILABLE:
            level_info = [
                "Легкий: швидший рух (+30%)",
                "Середній: звичайний рух",
                "Важкий: повільний рух (-30%)"
            ]

            for i, info in enumerate(level_info):
                color = YELLOW if i == self.selected_option else GRAY
                text = small_font.render(info, True, color)
                text_rect = text.get_rect(center=(self.WIDTH // 2, 450 + i * 20))
                self.screen.blit(text, text_rect)

    def render_pause_menu(self):
        """Рендеринг меню паузи"""
        # Напівпрозорий фон
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        font = pygame.font.Font(None, 48)
        small_font = pygame.font.Font(None, 24)

        # Текст паузи
        pause_text = font.render("ПАУЗА", True, (255, 255, 255))
        pause_rect = pause_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 - 50))
        self.screen.blit(pause_text, pause_rect)

        # Інструкції
        instruction = small_font.render("ПРОБІЛ - продовжити, ESC - меню", True, (255, 255, 255))
        instruction_rect = instruction.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 + 20))
        self.screen.blit(instruction, instruction_rect)

    def render_completion_screen(self):
        """Рендеринг екрану завершення"""
        self.screen.fill((0, 0, 0))

        font = pygame.font.Font(None, 48)
        small_font = pygame.font.Font(None, 24)

        # Повідомлення про перемогу
        win_text = font.render("РІВЕНЬ ПРОЙДЕНО!", True, (0, 255, 0))
        win_rect = win_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 - 50))
        self.screen.blit(win_text, win_rect)

        # Складність
        if self.current_difficulty:
            diff_text = small_font.render(f"Складність: {self.current_difficulty.value}", True, (255, 255, 255))
            diff_rect = diff_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
            self.screen.blit(diff_text, diff_rect)

        # Інструкція
        instruction = small_font.render("ПРОБІЛ - повернутися до меню", True, (255, 255, 255))
        instruction_rect = instruction.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 + 50))
        self.screen.blit(instruction, instruction_rect)

    def run(self):
        """Головний цикл гри"""
        print(f"🎮 Запуск 3D Лабіринт...")
        if PATTERNS_AVAILABLE:
            print("✅ Design Patterns активні")
        else:
            print("⚠️ Design Patterns недоступні, стандартний режим")

        while self.running:
            dt = self.clock.tick(self.FPS) / 1000.0

            self.handle_events()
            self.update(dt)
            self.render()

        pygame.quit()
        sys.exit()


class SimpleRenderer:
    """Простий рендерер для fallback режиму"""

    def __init__(self, screen):
        self.screen = screen

    def render_3d_view(self, rays, player_angle=0):
        """Простий 3D рендеринг"""
        WIDTH, HEIGHT = self.screen.get_size()

        # Небо
        pygame.draw.rect(self.screen, (80, 80, 120), (0, 0, WIDTH, HEIGHT // 2))

        # Підлога
        pygame.draw.rect(self.screen, (40, 40, 40), (0, HEIGHT // 2, WIDTH, HEIGHT // 2))

        # Стіни
        if rays:
            strip_width = WIDTH / len(rays)

            for i, ray in enumerate(rays):
                distance = ray.get('distance', 15)
                if distance <= 0:
                    continue

                wall_height = min(HEIGHT, max(1, int(HEIGHT / distance)))
                wall_top = (HEIGHT - wall_height) // 2

                brightness = max(30, 255 - int(distance * 20))
                color = (brightness, brightness // 2, brightness // 4)

                rect = pygame.Rect(int(i * strip_width), wall_top,
                                   max(1, int(strip_width)), wall_height)
                pygame.draw.rect(self.screen, color, rect)

    def get_renderer_info(self):
        return {'type': 'SimpleRenderer'}