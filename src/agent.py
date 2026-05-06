import random
import numpy as np
import torch
from collections import deque
from src.model import LinearQNet
from src.trainer import QTrainer
from pygame.math import Vector2

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001
EPSILON = 0.01     # Tham số exploration
GAMMA = 0.9     # Discount rate
INPUT_SIZE = 11
HIDDEN_SIZE = 256
OUTPUT_SIZE = 3


class Agent:
    def __init__(self, model_path: str = None):
        self.n_games = 0
        self.epsilon = 0          
        self.gamma = 0.9          
        self.memory = deque(maxlen=MAX_MEMORY)

        self.model = LinearQNet(input_size=INPUT_SIZE, hidden_size=HIDDEN_SIZE, output_size=OUTPUT_SIZE)
        if model_path:
            self.model.load(model_path)

        self.trainer = QTrainer(self.model, learning_rate=LR, gamma=self.gamma)

    def get_state(self, game):
        return game.get_state()

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state, training: bool = True):
        """
        Epsilon-greedy policy.
        training=False -> luôn chọn action tốt nhất (dùng khi watch AI).
        """
        if training:
            self.epsilon = max(0, 80 - self.n_games)
        else:
            self.epsilon = 0

        final_move = [0, 0, 0]

        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move