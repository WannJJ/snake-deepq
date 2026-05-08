import os
import torch
import torch.nn as nn


class LinearQNet(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = torch.relu(self.linear1(x))
        x = self.linear2(x)
        return x

    def save(self, file_path: str = "checkpoints/model.pth"):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        torch.save(self.state_dict(), file_path)

    def load(self, file_path: str = "checkpoints/model.pth", device="cpu") -> bool:
        if os.path.exists(file_path):
            self.load_state_dict(torch.load(file_path, map_location=device, weights_only=True))
            self.to(device)
            self.eval()
            return True
        return False