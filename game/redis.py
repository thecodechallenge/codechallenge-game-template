import json
import logging
import redis

from game.game import Game
from game.exceptions import GameNotFoundInRedis
from game.environment import DB, DECODE_RESPONSES, REDIS_URL
from game.redis_constants import DEFAULT_EXPIRE, REDIS_GAME_KEY_PREFIX


def create_redis_client():
    return redis.Redis.from_url(url=REDIS_URL, db=DB, decode_responses=DECODE_RESPONSES)


redis_client = create_redis_client()


def set_game(game: Game) -> bool:
    try:
        return redis_client.set(
            REDIS_GAME_KEY_PREFIX + game.game_id,
            json.dumps(game.to_dict()),
            ex=DEFAULT_EXPIRE,
        )
    except redis.RedisError as exc:
        logging.exception(f'Error writing game to redis: {exc}')
        return False


async def remove_game(game_id: str):
    try:
        return redis_client.delete(REDIS_GAME_KEY_PREFIX + game_id)
    except redis.RedisError as exc:
        logging.exception(f'Error deleting game from redis: {exc}')
        return False


def get_game(game_id: str) -> Game:
    try:
        data = redis_client.get(REDIS_GAME_KEY_PREFIX + game_id)
        if data is None:
            raise GameNotFoundInRedis()
        return Game.from_dict(json.loads(data))
    except redis.RedisError as exc:
        logging.exception(f'Error reading game from redis: {exc}')
        raise GameNotFoundInRedis()
