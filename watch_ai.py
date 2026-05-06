import sys
from src.agent import Agent
from src.game import SnakeGameAI
from src.plotter import Plotter
from src.score_manager import ScoreManager

RENDER = True # Để render=True nếu muốn quan sát AI học, render=False để train siêu nhanh
SPEED = 250

def train(resume_model: str = None):
    plotter = Plotter()
    scores = ScoreManager()
    agent = Agent(model_path=resume_model)
    game = SnakeGameAI(render=RENDER, speed=SPEED, ai_mode=True)
    
    game.state = "PLAYING"

    total_score = 0
    record = scores.get_ai_highscore()

    print("🤖 TRAINING MODE")
    print(f"Current AI High Score: {record}")


    try:
        while True:
            state_old = agent.get_state(game)
            action = agent.get_action(state_old, training=False)

            reward, done, score, state_new = game.play_step(action)

            if RENDER:
                game.draw()
                game.clock.tick(SPEED)

            if done:
                game.reset_game()
                agent.n_games += 1

                total_score += score
                mean_score = total_score / agent.n_games

                if score > record:
                    record = score
                    scores.update_ai_highscore(record)
                    print(f"✅ Game {agent.n_games:>4} | 🏆 NEW RECORD: {record}")
                else:
                    print(
                        f"✅ Game {agent.n_games:>4} | "
                        f"Score: {score:>3} | Mean: {mean_score:.2f} | Record: {record}"
                    )

                plotter.plot(score, mean_score)

                # Restart game
                game.state = "PLAYING"

    except KeyboardInterrupt:
        print("\n🛑 Training interrupted.")
        plotter.save(path="records/performing_plot.png")
        plotter.close()
        print("💾 Plot saved!")


if __name__ == "__main__":
    model_path = sys.argv[1] if len(sys.argv) > 1 else None
    train(resume_model=model_path)