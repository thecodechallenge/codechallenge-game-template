from typing import Dict, List

import requests
from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from uvicorn.config import logger

from game.manager import Manager
from game.exceptions import GameNotFoundInRedis, InvalidQuantityPlayers
from game.environment import (
    WEB_REGISTRY_URL,
    GAME_PUBLIC_URL,
    GAME_REGISTRATION_TOKEN,
)
from game import GAME_NAME, GAME_DISPLAY_NAME, GAME_DESCRIPTION


MANAGER = Manager()
app = FastAPI()
router = APIRouter()


@app.on_event("startup")
def register_with_web():
    """Announce this game to the web's games registry (best-effort)."""
    try:
        requests.post(
            f"{WEB_REGISTRY_URL}/games/register/",
            json={
                'name': GAME_NAME,
                'display_name': GAME_DISPLAY_NAME,
                'url': GAME_PUBLIC_URL,
                'description': GAME_DESCRIPTION,
            },
            headers={'X-Registration-Token': GAME_REGISTRATION_TOKEN},
            timeout=5,
        )
        logger.info(f"Registered '{GAME_NAME}' with the web at {WEB_REGISTRY_URL}")
    except requests.RequestException as exc:
        logger.error(f"Could not self-register '{GAME_NAME}' with the web: {exc}")


class CreateRequest(BaseModel):
    players: List[str]


class ExecuteActionRequest(BaseModel):
    game_data: Dict


def _error(message: str, status: int) -> JSONResponse:
    return JSONResponse(
        {'status': 'ERROR', 'code': status, 'message': message},
        status_code=status,
    )


# The four endpoints the match server calls. You usually don't touch these;
# the game rules live in game/game.py and game/manager.py.

@router.post("/games")
async def create(create_request: CreateRequest):
    try:
        return JSONResponse(MANAGER.create_game(create_request.players))
    except InvalidQuantityPlayers as exc:
        return _error(f'InvalidQuantityPlayers: {exc}', 400)
    except Exception as exc:
        return _error(f'Unhandled exception ocurred: {exc}', 500)


@router.post("/games/{game_id}/actions")
async def execute_action(game_id: str, execute_request: ExecuteActionRequest):
    try:
        return JSONResponse(MANAGER.process_request(game_id, execute_request.game_data))
    except GameNotFoundInRedis as exc:
        return _error(f'GameNotFoundInRedis: {exc}', 404)
    except Exception as exc:
        return _error(f'Unhandled exception ocurred: {exc}', 500)


@router.post("/games/{game_id}/penalizes")
async def penalize(game_id: str):
    try:
        return JSONResponse(MANAGER.penalize(game_id))
    except GameNotFoundInRedis as exc:
        return _error(f'GameNotFoundInRedis: {exc}', 404)
    except Exception as exc:
        return _error(f'Unhandled exception ocurred: {exc}', 500)


@router.post("/games/{game_id}/abort")
async def abort(game_id: str):
    try:
        return JSONResponse(MANAGER.abort(game_id))
    except GameNotFoundInRedis as exc:
        return _error(f'GameNotFoundInRedis: {exc}', 404)
    except Exception as exc:
        return _error(f'Unhandled exception ocurred: {exc}', 500)


app.include_router(router)
