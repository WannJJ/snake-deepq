import pygame
from pygame.math import Vector2
from src.game import SnakeGameAI, Direction, SnakeGame
from src.score_manager import ScoreManager

SPEED = 80 # Tốc độ vừa phải cho người chơi

def get_human_action(game):
    """
    Chuyển phím WASD/Arrow thành action [thẳng, phải, trái]
    dựa trên hướng hiện tại của rắn.
    """
    keys = pygame.key.get_pressed()
    curr = game.snake.direction

    desired = curr
    if (keys[pygame.K_UP] or keys[pygame.K_w]  or keys[pygame.K_KP8]) and curr.y != 1:
        desired = Vector2(0, -1)
    elif (keys[pygame.K_DOWN] or keys[pygame.K_s] or keys[pygame.K_KP2]) and curr.y != -1:
        desired = Vector2(0, 1)
    elif (keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_KP4]) and curr.x != 1:
        desired = Vector2(-1, 0)
    elif (keys[pygame.K_RIGHT] or keys[pygame.K_d] or keys[pygame.K_KP6]) and curr.x != -1:
        desired = Vector2(1, 0)

    return desired

def play():
    pygame.init()
    #game = SnakeGameAI(render=True, speed=SPEED)  
    game = SnakeGame(render=True, speed=SPEED)
    scores = ScoreManager()

    print("🎮 HUMAN MODE")
    print(f"High Score: {scores.get_human_highscore()}")
    print("WASD / Arrow Keys để di chuyển. ESC để thoát.\n")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif game.state == "MENU" and event.key == pygame.K_SPACE:
                    game.state = "PLAYING"
                elif game.state == "GAMEOVER" and event.key == pygame.K_SPACE:
                    game.reset_game()
                    game.state = "PLAYING"
                elif game.state == "PLAYING":                    
                    action = get_human_action(game)
                    reward, done, score, state = game.play_step(action)

                    if done:
                        print(f"💀 Game Over! Score: {score}")
                        if scores.update_human_highscore(score):
                            print(f"🏆 New High Score: {score}!")
                        #game.reset_game()
        game.update()
        game.draw()
        game.clock.tick(SPEED)
                    

    pygame.quit()


if __name__ == "__main__":
    play()