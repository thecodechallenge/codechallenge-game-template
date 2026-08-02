import uuid
import random
from typing import Dict, List

from game.exceptions import InvalidData
from game.player import Player
from game import (
    SIDE,
    TOTAL_MOVES,
    EMPTY,
    SCORE_PENALTY,
    SCORE_FORCE_GAMEOVER,
)


class Game:
    """Example turn-based game: **Sum Battle**.

    Each turn the current player submits a number 1..10, added to their score.
    After TOTAL_MOVES turns the higher score wins.

    Replace the marked sections with your own rules. The rest of the file
    (turn handling, serialization, the Manager/server around it) is the plumbing
    the platform needs and can usually stay as-is.
    """

    def __init__(self, players_names: List[str] = None) -> None:
        if players_names:
            self.game_id = str(uuid.uuid1())
            self.players = self.create_players(players_names)
            self.current_player = self.players[0]
            self.remaining_moves = TOTAL_MOVES
            self.loser = None
            # ---- TODO: initialise your own game state here ----
            self.history = []   # list of [side, number] for the board render
            # ---------------------------------------------------
        else:
            # Empty instance used when reloading from redis.
            self.game_id = ''
            self.players = []
            self.current_player = None
            self.remaining_moves = 0
            self.loser = None
            self.history = []

    @staticmethod
    def create_players(names: List[str]) -> List[Player]:
        names = list(names)
        random.shuffle(names)
        return [Player(name, side) for name, side in zip(names, SIDE)]

    # ----- turn / state (usually keep as-is) --------------------------------

    def get_current_player_name(self) -> str:
        return EMPTY if self.game_over() else self.current_player.name

    def get_current_player_side(self) -> str:
        return self.current_player.side

    def next_player_turn(self) -> Player:
        index = self.players.index(self.current_player)
        return self.players[(index + 1) % len(self.players)]

    def next_turn(self) -> None:
        self.current_player = self.next_player_turn()
        self.remaining_moves -= 1

    def penalize_player(self) -> None:
        player = self.current_player
        player.add_score(SCORE_PENALTY)
        if player.score < SCORE_FORCE_GAMEOVER or player.if_lost_for_timeout():
            if player.if_lost_for_timeout():
                player.score = 0
            self.loser = player
            self.remaining_moves = 0

    def get_winner(self) -> str:
        if not self.game_over():
            return EMPTY
        ranked = sorted(self.players, key=lambda p: p.score, reverse=True)
        return 'tie' if ranked[0].score == ranked[1].score else ranked[0].name

    def get_turn_data(self) -> Dict:
        turn_data = {
            'board': self.get_board_str(),
            'remaining_moves': self.remaining_moves,
        }
        turn_data.update(self.current_player.get_current_player_data())
        for index, player in enumerate(self.players, 1):
            turn_data.update(player.get_player_data(index))
        if self.game_over():
            turn_data['winner'] = self.get_winner()
        return turn_data

    def get_play_data(self, action_data: Dict) -> Dict:
        play_data = self.get_turn_data()
        play_data.update(action_data)
        return play_data

    # ===================================================================
    # TODO: everything below is your game. Replace it.
    # ===================================================================

    def game_over(self) -> bool:
        return self.remaining_moves <= 0 or self.loser is not None

    def get_board_str(self) -> str:
        """A human/bot-readable view of the state, sent every turn."""
        if not self.history:
            return '(no moves yet)'
        return ' '.join(f'{side}:{number}' for side, number in self.history)

    def move(self, number=None) -> None:
        """Apply the current player's move. Raise a PunishableError on a bad move."""
        try:
            number = int(number)
        except (TypeError, ValueError):
            raise InvalidData(f'number must be an integer, got {number!r}')
        if not 1 <= number <= 10:
            raise InvalidData('number must be between 1 and 10')
        self.current_player.add_score(number)
        self.history.append([self.current_player.side, number])

    def to_dict(self) -> Dict:
        """Serialize the full game state for redis (JSON-friendly)."""
        return {
            'game_id': self.game_id,
            'current_player': self.get_current_player_side(),
            'remaining_moves': self.remaining_moves,
            'loser': self.loser.side if self.loser else None,
            'players': [
                {
                    'name': p.name,
                    'side': p.side,
                    'score': p.score,
                    'penalize_counter': p.penalize_counter,
                }
                for p in self.players
            ],
            # ---- TODO: add your own state fields here ----
            'history': self.history,
            # ----------------------------------------------
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Game':
        """Rebuild a game from its serialized state."""
        game = cls()
        game.game_id = data['game_id']
        game.remaining_moves = data['remaining_moves']
        game.players = []
        for entry in data['players']:
            player = Player(entry['name'], entry['side'])
            player.score = entry['score']
            player.penalize_counter = entry['penalize_counter']
            game.players.append(player)
        game.current_player = next(
            p for p in game.players if p.side == data['current_player']
        )
        loser_side = data.get('loser')
        game.loser = next(
            (p for p in game.players if p.side == loser_side), None
        )
        # ---- TODO: restore your own state fields here ----
        game.history = data.get('history', [])
        # --------------------------------------------------
        return game
