from typing import Dict


class Player:
    def __init__(self, name: str, side: str) -> None:
        self.name = name
        self.side = side
        self.score = 0
        self.penalize_counter = 0

    def timeout_penalize(self):
        self.penalize_counter += 1

    def add_score(self, score):
        self.score += score

    def if_lost_for_timeout(self):
        return self.penalize_counter >= 10

    def get_current_player_data(self) -> Dict:
        return {'side': self.side}

    def get_player_data(self, pos: int) -> Dict:
        return {
            f'player_{pos}': self.name,
            f'score_{pos}': self.score,
        }
