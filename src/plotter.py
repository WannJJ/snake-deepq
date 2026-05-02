import matplotlib.pyplot as plt


class Plotter:
    def __init__(self):
        plt.ion()
        self.scores = []
        self.mean_scores = []
        self.fig, self.ax = plt.subplots(figsize=(10, 6))

        self.line_score, = self.ax.plot([], [], label="Score")
        self.line_mean, = self.ax.plot([], [], label="Mean Score")

        self.ax.set_xlabel("Games")
        self.ax.set_ylabel("Score")
        self.ax.set_title("Training Progress")
        self.ax.legend()
        self.ax.set_ylim(bottom=0)

    def plot(self, score: float, mean_score: float):
        self.scores.append(score)
        self.mean_scores.append(mean_score)

        self.line_score.set_data(range(len(self.scores)), self.scores)
        self.line_mean.set_data(range(len(self.mean_scores)), self.mean_scores)

        self.ax.set_xlim(0, max(1, len(self.scores)))
        self.ax.set_ylim(0, max(10, max(self.scores) + 5))

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.pause(0.1)

    def save(self, path: str = "records/training_plot.png"):
        self.fig.savefig(path)

    def close(self):
        plt.close(self.fig)