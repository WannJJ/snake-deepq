import json
import os

RECORDS_DIR = "records"


class ScoreManager:
    def __init__(self):
        os.makedirs(RECORDS_DIR, exist_ok=True)
        self.human_file = os.path.join(RECORDS_DIR, "human_highscore.json")
        self.ai_file = os.path.join(RECORDS_DIR, "ai_highscore.json")

    def _load(self, filepath: str) -> int:
        if not os.path.exists(filepath):
            return 0
        with open(filepath, "r") as f:
            return json.load(f).get("highscore", 0)

    def _save(self, filepath: str, score: int):
        with open(filepath, "w") as f:
            json.dump({"highscore": score}, f)

    # --- Human ---
    def get_human_highscore(self) -> int:
        return self._load(self.human_file)

    def update_human_highscore(self, score: int) -> bool:
        if score > self.get_human_highscore():
            self._save(self.human_file, score)
            return True
        return False

    # --- AI ---
    def get_ai_highscore(self) -> int:
        return self._load(self.ai_file)

    def update_ai_highscore(self, score: int) -> bool:
        if score > self.get_ai_highscore():
            self._save(self.ai_file, score)
            return True
        return False