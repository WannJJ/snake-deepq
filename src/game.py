import pygame
import random
import numpy as np
from enum import Enum
from collections import namedtuple

pygame.init()
font = pygame.font.SysFont("arial", 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple("Point", "x, y")

# Màu sắc
COLOR_BG = (20, 20, 20)
COLOR_SNAKE_HEAD = (0, 255, 150)
COLOR_SNAKE_BODY = (0, 200, 120)
COLOR_FOOD = (255, 80, 80)
COLOR_TEXT = (255, 255, 255)

BLOCK_SIZE = 20


class SnakeGameAI:
    def __init__(self, width=640, height=480, render=True, speed=40):
        self.width = width
        self.height = height
        self.render = render
        self.speed = speed

        if self.render:
            self.display = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("Snake Deep Q-Learning")
            self.clock = pygame.time.Clock()

        self.reset()

    def reset(self):
        """Khởi tạo lại game về trạng thái ban đầu."""
        self.direction = Direction.RIGHT
        self.head = Point(self.width / 2, self.height / 2)
        self.snake = [
            self.head,
            Point(self.head.x - BLOCK_SIZE, self.head.y),
            Point(self.head.x - (2 * BLOCK_SIZE), self.head.y),
        ]
        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0

    def _place_food(self):
        """Đặt thức ăn ngẫu nhiên, tránh rơi vào thân rắn."""
        cols = self.width // BLOCK_SIZE
        rows = self.height // BLOCK_SIZE
        while True:
            x = random.randint(0, cols - 1) * BLOCK_SIZE
            y = random.randint(0, rows - 1) * BLOCK_SIZE
            self.food = Point(x, y)
            if self.food not in self.snake:
                break

    def play_step(self, action):
        """
        action: [thẳng, phải, trái]
        Trả về: reward, game_over, score, state
        """
        self.frame_iteration += 1

        # Xử lý sự kiện thoát
        if self.render:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

        # Di chuyển
        self._move(action)
        self.snake.insert(0, self.head)

        reward = 0
        game_over = False

        # Kiểm tra va chạm hoặc đi lòng vòng quá lâu
        if self.is_collision() or self.frame_iteration > 100 * len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score, self.get_state()

        # Ăn thức ăn
        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()

        # Cập nhật màn hình
        if self.render:
            self._update_ui()
            self.clock.tick(self.speed)

        return reward, game_over, self.score, self.get_state()

    def is_collision(self, point=None):
        """Kiểm tra va chạm tường hoặc tự cắn."""
        if point is None:
            point = self.head

        if (
            point.x < 0
            or point.x >= self.width
            or point.y < 0
            or point.y >= self.height
        ):
            return True
        if point in self.snake[1:]:
            return True
        return False

    def _update_ui(self):
        """Vẽ game lên màn hình."""
        self.display.fill(COLOR_BG)

        for i, pt in enumerate(self.snake):
            color = COLOR_SNAKE_HEAD if i == 0 else COLOR_SNAKE_BODY
            pygame.draw.rect(
                self.display, color, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE)
            )
            pygame.draw.rect(
                self.display,
                (50, 50, 50),
                pygame.Rect(pt.x + 2, pt.y + 2, BLOCK_SIZE - 4, BLOCK_SIZE - 4),
            )

        pygame.draw.rect(
            self.display,
            COLOR_FOOD,
            pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE),
        )

        text = font.render(f"Score: {self.score}", True, COLOR_TEXT)
        self.display.blit(text, (10, 10))
        pygame.display.flip()

    def _move(self, action):
        """
        Chuyển action [thẳng, phải, trái] thành hướng di chuyển mới.
        """
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):          # Đi thẳng
            new_dir = clock_wise[idx]
        elif np.array_equal(action, [0, 1, 0]):        # Rẽ phải
            new_dir = clock_wise[(idx + 1) % 4]
        else:                                           # Rẽ trái
            new_dir = clock_wise[(idx - 1) % 4]

        self.direction = new_dir

        x, y = self.head.x, self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)

    def get_state(self):
        """
        Trả về numpy array 11 giá trị boolean:
        [danger_straight, danger_right, danger_left,
         dir_left, dir_right, dir_up, dir_down,
         food_left, food_right, food_up, food_down]
        """
        head = self.snake[0]
        point_l = Point(head.x - BLOCK_SIZE, head.y)
        point_r = Point(head.x + BLOCK_SIZE, head.y)
        point_u = Point(head.x, head.y - BLOCK_SIZE)
        point_d = Point(head.x, head.y + BLOCK_SIZE)

        dir_l = self.direction == Direction.LEFT
        dir_r = self.direction == Direction.RIGHT
        dir_u = self.direction == Direction.UP
        dir_d = self.direction == Direction.DOWN

        state = [
            # Nguy hiểm phía trước
            (dir_r and self.is_collision(point_r))
            or (dir_l and self.is_collision(point_l))
            or (dir_u and self.is_collision(point_u))
            or (dir_d and self.is_collision(point_d)),
            # Nguy hiểm bên phải
            (dir_u and self.is_collision(point_r))
            or (dir_d and self.is_collision(point_l))
            or (dir_l and self.is_collision(point_u))
            or (dir_r and self.is_collision(point_d)),
            # Nguy hiểm bên trái
            (dir_d and self.is_collision(point_r))
            or (dir_u and self.is_collision(point_l))
            or (dir_r and self.is_collision(point_u))
            or (dir_l and self.is_collision(point_d)),
            # Hướng hiện tại
            dir_l, dir_r, dir_u, dir_d,
            # Vị trí thức ăn
            self.food.x < self.head.x,  # trái
            self.food.x > self.head.x,  # phải
            self.food.y < self.head.y,  # trên
            self.food.y > self.head.y,  # dưới
        ]

        return np.array(state, dtype=int)