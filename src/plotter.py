import matplotlib.pyplot as plt
import time

class Plotter:
    WINDOW_SIZE = 20

    def __init__(self):
        plt.ion()
        self.scores = []
        self.ma20_scores = []
        self.fig, self.ax = plt.subplots(figsize=(10, 6))

        self.line_score, = self.ax.plot([], [], label="Score")
        self.line_ma20, = self.ax.plot([], [], label="Mean (Last 20 Games)")

        self.ax.set_xlabel("Games")
        self.ax.set_ylabel("Score")
        self.ax.set_title("Training Progress")
        self.ax.legend()
        self.ax.set_ylim(bottom=0)

    def plot(self, score: float):
        self.scores.append(score)

        # Tính moving average
        recent = self.scores[-self.WINDOW_SIZE:]
        self.ma20_scores.append(sum(recent) / len(recent))


        self.line_score.set_data(range(len(self.scores)), self.scores)
        self.line_ma20.set_data(range(len(self.scores)), self.ma20_scores)

        self.ax.set_xlim(0, max(1, len(self.scores)))
        self.ax.set_ylim(0, max(10, max(self.scores) + 5))

        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
        time.sleep(0.5)


    def save(self, path: str = "records/training_plot.png"):
        import os
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Tắt interactive mode tạm thời để save an toàn
        was_ion = plt.isinteractive()
        if was_ion:
            plt.ioff()
        
        try:
            self.fig.savefig(path)
        finally:
            if was_ion:
                plt.ion()

    def close(self):
        plt.close(self.fig)