import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

class QTrainer:
    def __init__(self, model: nn.Module, learning_rate: float, gamma: float, device):
        self.model = model
        self.gamma = gamma
        self.device = device
        self.optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        self.criterion = nn.MSELoss()
        """
        for i in self.model.parameters():
            print(i.is_cuda)
        """

    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(np.array(state), dtype=torch.float).to(self.device)
        next_state = torch.tensor(np.array(next_state), dtype=torch.float).to(self.device)
        action = torch.tensor(np.array(action), dtype=torch.long).to(self.device)
        reward = torch.tensor(np.array(reward), dtype=torch.float).to(self.device)

        # Nếu là single experience, thêm batch dimension
        if len(state.shape) == 1:
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done,)

        # 1. Q(s,a) hiện tại
        pred = self.model(state)

        # 2. Q_target = reward + gamma * max(Q(s'))
        target = pred.clone()
        for idx in range(len(done)):
            q_new = reward[idx]
            if not done[idx]:
                q_new = reward[idx] + self.gamma * torch.max(
                    self.model(next_state[idx])
                )
            target[idx][torch.argmax(action[idx]).item()] = q_new

        # 3. Backpropagation
        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()
        self.optimizer.step()