import pygame
import random
import numpy as np
from enum import Enum
from collections import namedtuple
import math
from pygame.math import Vector2
from src.score_manager import ScoreManager

pygame.init()


# --- Constants ---
CELL_SIZE = 30
CELL_NUMBER = 20
SCREEN_WIDTH = CELL_NUMBER * CELL_SIZE
SCREEN_HEIGHT = CELL_NUMBER * CELL_SIZE + 80  # Thêm chỗ cho UI

FPS = 60

# --- Màu sắc & Gradient ---
BG_TOP = (15, 23, 42)
BG_BOTTOM = (30, 41, 59)
SNAKE_HEAD = (52, 211, 153)
SNAKE_BODY = (16, 185, 129)
SNAKE_OUTLINE = (6, 78, 59)
FOOD_COLOR = (248, 113, 113)
FOOD_GLOW = (220, 38, 38)
TEXT_COLOR = (241, 245, 249)
ACCENT = (56, 189, 248)
GOLD = (250, 204, 21)

# --- Font ---
try:
    font_score = pygame.font.Font(None, 48)
    font_title = pygame.font.Font(None, 72)
    font_sub = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 28)
except:
    font_score = pygame.font.SysFont("consolas", 48)
    font_title = pygame.font.SysFont("consolas", 72)
    font_sub = pygame.font.SysFont("consolas", 36)
    font_small = pygame.font.SysFont("consolas", 28)

class Direction(Enum):
    RIGHT = Vector2(1, 0)
    LEFT = Vector2(-1, 0)
    UP = Vector2(0, -1)
    DOWN = Vector2(0, 1)

# --- Hiệu ứng Particle ---
class Particle:
    def __init__(self, pos, color, speed, life):
        self.pos = Vector2(pos)
        angle = random.uniform(0, math.pi * 2)
        self.vel = Vector2(math.cos(angle), math.sin(angle)) * speed
        self.color = color
        self.life = life
        self.max_life = life
        self.size = random.randint(4, 8)

    def update(self):
        self.pos += self.vel
        self.life -= 1
        self.size = max(1, self.size - 0.1)

    def draw(self, screen):
        alpha = int(255 * (self.life / self.max_life))
        s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
        screen.blit(s, (int(self.pos.x - self.size), int(self.pos.y - self.size)))

# --- Rắn ---
class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.body = [Vector2(12, 12), Vector2(11, 12), Vector2(10, 12)]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.grow = False
        self.alive = True
        self.move_timer = 0
        self.move_delay = 8  # Càng nhỏ càng nhanh
        self.base_delay = 8

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_KP8, pygame.K_w) and self.direction.y != 1:
                self.next_direction = Direction.UP
            elif event.key in (pygame.K_DOWN, pygame.K_KP2, pygame.K_s) and self.direction.y != -1:
                self.next_direction = Direction.DOWN
            elif event.key in (pygame.K_LEFT, pygame.K_KP4, pygame.K_a) and self.direction.x != 1:
                self.next_direction = Direction.LEFT
            elif event.key in (pygame.K_RIGHT, pygame.K_KP6, pygame.K_d) and self.direction.x != -1:
                self.next_direction = Direction.RIGHT
    def _move(self, action):
        """
        Chuyển action [thẳng, phải, trái] thành Direction (UP, RIGHT, LEFT, DOWN)
        """
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):          # Đi thẳng
            new_dir = clock_wise[idx]
        elif np.array_equal(action, [0, 1, 0]):        # Rẽ phải
            new_dir = clock_wise[(idx + 1) % 4]
        else:                                           # Rẽ trái
            new_dir = clock_wise[(idx - 1) % 4]
        self.next_direction = new_dir

    def is_collision(self, dir):
        new_head = self.body[0] + dir.value

        # Va chạm tường
        if not (0 <= new_head.x < CELL_NUMBER and 0 <= new_head.y < CELL_NUMBER):
            return True

        # Va chạm thân
        if new_head in self.body[:-1]:
            return True
        
        return False
        
    def update(self):
        if not self.alive:
            return

        self.move_timer += 1
        if self.move_timer < self.move_delay:
            return
        self.move_timer = 0

        self.direction = self.next_direction
        new_head = self.body[0] + self.direction.value

        # Va chạm tường
        if not (0 <= new_head.x < CELL_NUMBER and 0 <= new_head.y < CELL_NUMBER):
            self.alive = False
            return

        # Va chạm thân
        if new_head in self.body[:-1]:
            self.alive = False
            return

        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False

        # Tăng tốc dần
        self.move_delay = max(3, self.base_delay - len(self.body) // 6)

    def grow_snake(self):
        self.grow = True

    def draw(self, screen):
        for i, segment in enumerate(self.body):
            x = int(segment.x * CELL_SIZE)
            y = int(segment.y * CELL_SIZE) + 80
            rect = pygame.Rect(x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2)

            # Gradient từ đầu đến đuôi
            ratio = i / max(len(self.body) - 1, 1)
            r = int(SNAKE_HEAD[0] * (1 - ratio) + SNAKE_BODY[0] * ratio)
            g = int(SNAKE_HEAD[1] * (1 - ratio) + SNAKE_BODY[1] * ratio)
            b = int(SNAKE_HEAD[2] * (1 - ratio) + SNAKE_BODY[2] * ratio)
            color = (r, g, b)

            # Glow effect
            glow_surf = pygame.Surface((CELL_SIZE + 8, CELL_SIZE + 8), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*color, 60), glow_surf.get_rect(), border_radius=10)
            screen.blit(glow_surf, (x - 4, y - 4))

            # Thân rắn
            pygame.draw.rect(screen, color, rect, border_radius=8)
            pygame.draw.rect(screen, SNAKE_OUTLINE, rect, width=2, border_radius=8)

            # Mắt cho đầu rắn
            if i == 0:
                eye_offset = 6
                pupil_offset = 8
                if self.direction == Direction.RIGHT:
                    eye1, eye2 = (x + 18, y + 8), (x + 18, y + 20)
                    pupil = (2, 0)
                elif self.direction == Direction.LEFT:
                    eye1, eye2 = (x + 10, y + 8), (x + 10, y + 20)
                    pupil = (-2, 0)
                elif self.direction == Direction.LEFT:
                    eye1, eye2 = (x + 8, y + 10), (x + 20, y + 10)
                    pupil = (0, -2)
                else:
                    eye1, eye2 = (x + 8, y + 20), (x + 20, y + 20)
                    pupil = (0, 2)

                for eye in [eye1, eye2]:
                    pygame.draw.circle(screen, (255, 255, 255), eye, 5)
                    pygame.draw.circle(screen, (15, 23, 42), (eye[0] + pupil[0], eye[1] + pupil[1]), 3)

# --- Mồi ---
class Food:
    def __init__(self): 
        self.pos = Vector2(0, 0)
        self.randomize()
        self.anim_offset = random.random() * math.pi * 2

    def randomize(self):
        self.pos = Vector2(random.randint(0, CELL_NUMBER - 1), random.randint(0, CELL_NUMBER - 1))

    def draw(self, screen, time):
        x = int(self.pos.x * CELL_SIZE)
        y = int(self.pos.y * CELL_SIZE) + 80
        center = (x + CELL_SIZE // 2, y + CELL_SIZE // 2)

        # Animation nhịp đập
        pulse = math.sin(time * 4 + self.anim_offset) * 3

        # Glow đỏ
        for radius, alpha in [(20, 30), (14, 60), (10, 120)]:
            glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*FOOD_GLOW, alpha), (radius, radius), radius)
            screen.blit(glow, (center[0] - radius, center[1] - radius))

        # Quả táo / mồi
        pygame.draw.circle(screen, FOOD_COLOR, center, 10 + pulse)
        pygame.draw.circle(screen, (180, 30, 30), center, 10 + pulse, width=2)

        # Lá nhỏ
        leaf_pos = (center[0] + 4, center[1] - 10 + pulse)
        pygame.draw.ellipse(screen, (34, 197, 94), (leaf_pos[0], leaf_pos[1], 8, 5))


# --- Game chính ---
class SnakeGameAI:
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, render=True, speed=FPS):
        self.width = width
        self.height = height
        self.render = render
        self.speed = speed

        if self.render:            
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("🐍 Snake Glow Edition")
            self.clock = pygame.time.Clock()

        scores = ScoreManager()
        self.highscore = scores.get_human_highscore()
        self.reset_game()
        self.state = "MENU"  # MENU, PLAYING, GAMEOVER
        self.particles = []
        self.time = 0

    def reset_game(self):
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.particles = []
        self.frame_iteration = 0

    def get_state(self):
        """
        Trả về numpy array 11 giá trị boolean:
        [danger_straight, danger_right, danger_left,
         dir_left, dir_right, dir_up, dir_down,
         food_left, food_right, food_up, food_down]
        """

        snake = self.snake
        dir = snake.direction
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(snake.direction)
        right_dir = clock_wise[(idx + 1) % 4]
        left_dir = clock_wise[(idx - 1) % 4]
        

        state = [
            # Nguy hiểm phía trước
            snake.is_collision(dir),

            # Nguy hiểm bên phải
            snake.is_collision(right_dir),

            # Nguy hiểm bên trái
            snake.is_collision(left_dir),

            # Hướng hiện tại
            dir == Direction.LEFT,
            dir == Direction.RIGHT,
            dir == Direction.UP,
            dir == Direction.DOWN,
            
            # Vị trí thức ăn
            self.food.pos.x < self.snake.body[0].x,  # trái
            self.food.pos.x > self.snake.body[0].x,  # phải
            self.food.pos.y < self.snake.body[0].y,  # trên
            self.food.pos.y > self.snake.body[0].y,  # dưới
        ]

        return np.array(state, dtype=int)
    
    def spawn_particles(self, pos):
        center = (pos.x * CELL_SIZE + CELL_SIZE // 2, pos.y * CELL_SIZE + CELL_SIZE // 2 + 80)
        for _ in range(15):
            self.particles.append(Particle(center, FOOD_COLOR, random.uniform(2, 5), random.randint(20, 40)))
        for _ in range(10):
            self.particles.append(Particle(center, GOLD, random.uniform(1, 3), random.randint(15, 30)))

    def draw_gradient_bg(self):
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(BG_TOP[0] * (1 - ratio) + BG_BOTTOM[0] * ratio)
            g = int(BG_TOP[1] * (1 - ratio) + BG_BOTTOM[1] * ratio)
            b = int(BG_TOP[2] * (1 - ratio) + BG_BOTTOM[2] * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

    def draw_grid(self):
        for x in range(0, SCREEN_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, (255, 255, 255, 15), (x, 80), (x, SCREEN_HEIGHT), 1)
        for y in range(80, SCREEN_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, (255, 255, 255, 15), (0, y), (SCREEN_WIDTH, y), 1)

    def draw_ui(self):
        # Panel nền UI
        pygame.draw.rect(self.screen, (15, 23, 42, 200), (0, 0, SCREEN_WIDTH, 80))
        pygame.draw.line(self.screen, ACCENT, (0, 78), (SCREEN_WIDTH, 78), 2)

        score_text = font_score.render(f"{self.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (30, 20))

        high_text = font_small.render(f"BEST: {self.highscore}", True, GOLD)
        self.screen.blit(high_text, (SCREEN_WIDTH - 140, 28))

        # Speed indicator
        speed_text = font_small.render(f"SPEED: {11 - self.snake.move_delay}", True, ACCENT)
        self.screen.blit(speed_text, (SCREEN_WIDTH // 2 - 50, 28))

    def draw_menu(self):
        self.draw_gradient_bg()
        title = font_title.render("SNAKE GLOW", True, SNAKE_HEAD)
        shadow = font_title.render("SNAKE GLOW", True, (0, 0, 0))
        self.screen.blit(shadow, (SCREEN_WIDTH // 2 - title.get_width() // 2 + 3, 203))
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))

        sub = font_sub.render("Press SPACE to play", True, ACCENT)
        pulse = math.sin(self.time * 3) * 5
        self.screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 320 + pulse))

        hint = font_small.render("⬆️⬇️⬅️➡️ to move", True, (148, 163, 184))
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 400))

        best = font_sub.render(f"High Score: {self.highscore}", True, GOLD)
        self.screen.blit(best, (SCREEN_WIDTH // 2 - best.get_width() // 2, 480))

    def draw_gameover(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        over = font_title.render("GAME OVER", True, FOOD_COLOR)
        self.screen.blit(over, (SCREEN_WIDTH // 2 - over.get_width() // 2, 220))

        sc = font_sub.render(f"Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(sc, (SCREEN_WIDTH // 2 - sc.get_width() // 2, 310))

        if self.score >= self.highscore and self.score > 0:
            new = font_sub.render("🎉 NEW RECORD!", True, GOLD)
            self.screen.blit(new, (SCREEN_WIDTH // 2 - new.get_width() // 2, 360))

        restart = font_sub.render("Press SPACE to play again", True, ACCENT)
        self.screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2, 430))

    def update(self):
        self.time += 0.016
        if self.state == "PLAYING":
            self.snake.update()

            if not self.snake.alive:
                if self.score > self.highscore:
                    self.highscore = self.score
                self.state = "GAMEOVER"
                return

            # Ăn mồi
            if self.snake.body[0] == self.food.pos:
                self.snake.grow_snake()
                self.score += 10
                self.spawn_particles(self.food.pos)
                self.food.randomize()
                # Đảm bảo mồi không spawn trên thân rắn
                while self.food.pos in self.snake.body:
                    self.food.randomize()

        # Update particles
        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)

    def draw(self):
        if self.state == "MENU":
            self.draw_menu()
        else:
            self.draw_gradient_bg()
            self.draw_grid()
            self.food.draw(self.screen, self.time)
            self.snake.draw(self.screen)
            for p in self.particles:
                p.draw(self.screen)
            self.draw_ui()
            if self.state == "GAMEOVER":
                self.draw_gameover()

        pygame.display.flip()

    def play_step(self, action):
        """
        action: [thẳng, phải, trái]
        Trả về: reward, game_over, score, state
        """
        self.time += 0.016
        reward = 0
        game_over = False

        if self.state == "PLAYING":
            self.frame_iteration = 0
            
            # Xử lý sự kiện thoát
            if self.render:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        quit()
            
            #Di chuyển
            self.snake._move(action)
            self.snake.update()


            # Kiểm tra va chạm hoặc đi lòng vòng quá lâu
            if not self.snake.alive or self.frame_iteration > 100 * len(self.snake.body):
                if self.score > self.highscore:
                    self.highscore = self.score
                game_over = True
                reward = -10
                self.state = "GAMEOVER"
                return reward, game_over, self.score, self.get_state()

            # Ăn thức ăn
            if self.snake.body[0] == self.food.pos:
                self.snake.grow_snake()
                self.score += 10
                reward = 10
                self.spawn_particles(self.food.pos)
                self.food.randomize()
                # Đảm bảo mồi không spawn trên thân rắn
                while self.food.pos in self.snake.body:
                    self.food.randomize()

            # Cập nhật màn hình
            
        
        # Update particles
        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)

        return reward, game_over, self.score, self.get_state()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif self.state == "MENU" and event.key == pygame.K_SPACE:
                        self.state = "PLAYING"
                    elif self.state == "GAMEOVER" and event.key == pygame.K_SPACE:
                        self.reset_game()
                        self.state = "PLAYING"
                    elif self.state == "PLAYING":
                        self.snake.handle_input(event)

            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
