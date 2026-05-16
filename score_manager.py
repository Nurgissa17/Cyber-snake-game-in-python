import json


class ScoreManager:
    def __init__(self, filename="scores.json"):
        self.filename = filename
        self.scores = self.load_scores()

    def load_scores(self):
        try:
            with open(self.filename, "r") as file:
                data = json.load(file)

            if isinstance(data, list):
                return data

            return []

        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []

    def save_score(self, name, score):
        if not name.strip():
            name = "Player"

        record = {
            "name": name.strip()[:15],
            "score": score
        }

        self.scores.append(record)
        self.scores = sorted(self.scores, key=lambda item: item["score"], reverse=True)

        try:
            with open(self.filename, "w") as file:
                json.dump(self.scores, file, indent=4)
        except OSError:
            print("Error: score file could not be saved.")

    def get_leaderboard(self):
        return self.scores

    def clear_scores(self):
        self.scores = []

        try:
            with open(self.filename, "w") as file:
                json.dump(self.scores, file, indent=4)
        except OSError:
            print("Error: score file could not be cleared.")
