import pygame
from src.game import SnakeGameAI, Direction
from src.score_manager import ScoreManager


def get_human_action(game):
    """
    Chuyển phím WASD/Arrow thành action [thẳng, phải, trái]
    dựa trên hướng hiện tại của rắn.
    """
    keys = pygame.key.get_pressed()
    curr = game.direction

    desired = None
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        desired = Direction.UP
    elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
        desired = Direction.DOWN
    elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
        desired = Direction.LEFT
    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        desired = Direction.RIGHT

    if not desired or desired == curr:
        return [1, 0, 0]  # đi thẳng

    clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
    curr_idx = clock_wise.index(curr)
    desired_idx = clock_wise.index(desired)
    diff = (desired_idx - curr_idx) % 4

    if diff == 1:
        return [0, 1, 0]   # rẽ phải
    if diff == 3:
        return [0, 0, 1]   # rẽ trái
    return [1, 0, 0]       # diff == 2 (quay đầu) -> bị bỏ qua, đi thẳng


def play():
    pygame.init()
    game = SnakeGameAI(render=True, speed=12)  # Tốc độ vừa phải cho người chơi
    scores = ScoreManager()

    print("🎮 HUMAN MODE")
    print(f"High Score: {scores.get_human_highscore()}")
    print("WASD / Arrow Keys để di chuyển. ESC để thoát.\n")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        action = get_human_action(game)
        reward, done, score, state = game.play_step(action)

        if done:
            print(f"💀 Game Over! Score: {score}")
            if scores.update_human_highscore(score):
                print(f"🏆 New High Score: {score}!")
            game.reset()

    pygame.quit()


if __name__ == "__main__":
    play()