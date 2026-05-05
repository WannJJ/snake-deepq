import sys
from src.agent import Agent
from src.game import SnakeGameAI
from src.plotter import Plotter
from src.score_manager import ScoreManager

RENDER = True
SPEED = 160

def train(resume_model: str = None):
    plotter = Plotter()
    scores = ScoreManager()
    agent = Agent(model_path=resume_model)

    # Để render=True nếu muốn quan sát AI học, render=False để train siêu nhanh
    game = SnakeGameAI(render=RENDER, speed=SPEED)
    
    game.state = "PLAYING"

    total_score = 0
    record = scores.get_ai_highscore()

    print("🤖 TRAINING MODE")
    print(f"Current AI High Score: {record}")
    print("Nhấn Ctrl+C để dừng và lưu model.\n")

    try:
        while True:
            state_old = agent.get_state(game)
            action = agent.get_action(state_old, training=True)

            reward, done, score, state_new = game.play_step(action)

            if RENDER:
                game.draw()
                game.clock.tick(SPEED)

            agent.train_short_memory(state_old, action, reward, state_new, done)
            agent.remember(state_old, action, reward, state_new, done)

            if done:
                game.reset_game()
                agent.n_games += 1
                agent.train_long_memory()

                total_score += score
                mean_score = total_score / agent.n_games

                if score > record:
                    record = score
                    scores.update_ai_highscore(record)
                    agent.model.save("checkpoints/model_best.pth")
                    print(f"✅ Game {agent.n_games:>4} | 🏆 NEW RECORD: {record}")
                else:
                    print(
                        f"✅ Game {agent.n_games:>4} | "
                        f"Score: {score:>3} | Mean: {mean_score:.2f} | Record: {record}"
                    )

                plotter.plot(score, mean_score)

                # Save checkpoint mỗi 50 games
                if agent.n_games % 50 == 0:
                    agent.model.save("checkpoints/model_checkpoint.pth")

    except KeyboardInterrupt:
        print("\n🛑 Training interrupted.")
        agent.model.save("checkpoints/model_last.pth")
        plotter.save()
        plotter.close()
        print("💾 Model & plot saved!")


if __name__ == "__main__":
    model_path = sys.argv[1] if len(sys.argv) > 1 else None
    train(resume_model=model_path)