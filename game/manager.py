import asyncio
from typing import List

from game.game import Game
from game.redis import remove_game, set_game, get_game
from game import (
    STATE,
    ABORT,
    INVALID_STATE,
    GAMEOVER_STATE,
    TIMEOUT,
    VALID_STATE,
    ACTION,
    DATA,
    PLAY_ACTION,
    NUMBER,
    INVALID_PENALIZE,
)
from game.exceptions import (
    PunishableError,
    NonPunishableError,
    InvalidActionError,
    InvalidData,
    InvalidQuantityPlayers,
)


class Manager:
    """Drives games and their persistence. Usually stays as-is; the only
    game-specific part is `execute_action` -> `make_move`."""

    def __init__(self) -> None:
        self.games = dict()
        self.action_data = dict()

    def create_game(self, players_names: List[str]) -> dict:
        if len(players_names) == 2:
            new_game = Game(players_names)
            self.add_game(new_game)
            return self.get_game_start(new_game)
        raise InvalidQuantityPlayers()

    def get_game_start(self, game: Game) -> dict:
        return {
            'game_id': game.game_id,
            'current_player': game.get_current_player_name(),
            'turn_data': game.get_turn_data(),
        }

    def get_game_state(self, game: Game, state: str) -> dict:
        play_data = game.get_play_data(self.action_data)
        play_data[STATE] = state
        return {
            'game_id': game.game_id,
            'current_player': game.get_current_player_name(),
            'turn_data': game.get_turn_data(),
            'play_data': play_data,
        }

    def add_game(self, game: Game) -> None:
        set_game(game)
        self.games[game.game_id] = game

    def remove_game_from_manager(self, game_id: str) -> None:
        try:
            asyncio.get_running_loop()
            asyncio.create_task(remove_game(game_id))
        except RuntimeError:
            pass
        self.games.pop(game_id, None)

    def process_request(self, game_id: str, api_data: dict) -> dict:
        current_game = self.find_game(game_id)
        state = INVALID_STATE
        try:
            self.execute_action(current_game, api_data)
        except PunishableError:
            current_game.penalize_player()
        except NonPunishableError:
            pass
        else:
            state = VALID_STATE
        current_game.next_turn()
        self.add_game(current_game)
        if self.check_game_over(current_game):
            state = GAMEOVER_STATE
        return self.get_game_state(current_game, state)

    def execute_action(self, game: Game, api_data: dict) -> None:
        # TODO: dispatch your action(s) here.
        if api_data.get(ACTION) == PLAY_ACTION:
            return self.make_move(game, api_data.get(DATA, {}))
        raise InvalidActionError()

    def make_move(self, game: Game, data: dict) -> None:
        # TODO: pull your move's fields out of `data` and apply them.
        number = self.get_number(data)
        self.action_data = {NUMBER: number}
        game.move(number=number)

    def get_number(self, data: dict):
        try:
            return data[NUMBER]
        except (KeyError, TypeError):
            raise InvalidData()

    def penalize(self, game_id: str) -> dict:
        current_game = self.find_game(game_id)
        current_game.current_player.timeout_penalize()
        current_game.penalize_player()
        current_game.next_turn()
        set_game(current_game)
        state = TIMEOUT
        if self.check_game_over(current_game):
            state = GAMEOVER_STATE
        self.action_data = INVALID_PENALIZE
        return self.get_game_state(current_game, state)

    def check_game_over(self, current_game: Game) -> bool:
        if current_game.game_over():
            self.remove_game_from_manager(current_game.game_id)
            return True
        return False

    def abort(self, game_id: str) -> dict:
        current_game = self.find_game(game_id)
        self.remove_game_from_manager(current_game.game_id)
        return self.get_game_state(current_game, ABORT)

    def find_game(self, game_id: str) -> Game:
        if game_id in self.games:
            return self.games[game_id]
        return get_game(game_id)
