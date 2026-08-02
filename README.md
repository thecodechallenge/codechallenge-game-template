# codechallenge-game-template

A starting point for building a **game backend** for
[The Code Challenge](https://codechallenge.up.railway.app). It's a small
FastAPI service that already speaks the platform's HTTP protocol, persists
games in Redis, and **registers itself** with the web on startup. It ships
with a trivial example game ("Sum Battle") for you to replace.

> Click **“Use this template”** on GitHub to create your own game repo.

## What you get

```
game/
  __init__.py     constants + your game's NAME / DISPLAY_NAME / DESCRIPTION   <- edit
  game.py         the game rules (the example: Sum Battle)                    <- edit
  manager.py      turn orchestration + action dispatch                        <- light edit
  player.py       a player (name, score, penalties)
  server.py       the HTTP endpoints + self-registration (usually leave as-is)
  redis.py        persistence (uses your Game.to_dict / from_dict)
  environment.py  env vars
run.py            uvicorn entrypoint
tests/            example unit tests
```

## The contract (what the match server calls)

Your service exposes four endpoints — already implemented in `server.py`:

| Method & path                | Handler                   | Body                          |
| ---------------------------- | ------------------------- | ----------------------------- |
| `POST /games`                | `Manager.create_game`     | `{ "players": ["a", "b"] }`   |
| `POST /games/{id}/actions`   | `Manager.process_request` | `{ "game_data": { ... } }`    |
| `POST /games/{id}/penalizes` | `Manager.penalize`        | —                             |
| `POST /games/{id}/abort`     | `Manager.abort`           | —                             |

**Action protocol** (`game_data`):

```json
{ "action": "play", "data": { "number": 7 } }
```

**Responses**: `POST /games` returns `{ game_id, current_player, turn_data }`;
the action endpoints return `{ game_id, current_player, turn_data, play_data }`.
`turn_data` is the view sent every turn (must include a `board` string,
`remaining_moves`, `side`, `player_1/2`, `score_1/2`); `play_data` is
`turn_data` plus the echoed action and a `state` (`valid` / `invalid` /
`gameover` / `timeout` / `game aborted`).

## Build your game

1. **`game/__init__.py`** — set `GAME_NAME` (a slug, used for routing),
   `GAME_DISPLAY_NAME`, `GAME_DESCRIPTION`, your constants, and your action
   name(s) / data keys.
2. **`game/game.py`** — implement the rules. The methods the platform needs:
   - `move(**action_data)` — apply a turn; raise a `PunishableError`
     (e.g. `InvalidData`) on an illegal move (the player gets penalized).
   - `game_over()`, `get_winner()`, `get_board_str()`.
   - `to_dict()` / `from_dict()` — serialize state for Redis.
   The turn/score plumbing above the `TODO` line can usually stay.
3. **`game/manager.py`** — in `execute_action` / `make_move`, map your action
   name and pull your fields out of `data`.
4. **`tests/test_game.py`** — adjust the example tests.

## Self-registration

On startup the service POSTs to the web's `/games/register/` with its name,
public URL and description, so it shows up automatically. **Registration
requires a token** (sent as the `X-Registration-Token` header) — request it
from a Code Challenge admin (it's shown on the web's Games admin screen).
Configure:

| Env var                   | Meaning                                            | Local default              |
| ------------------------- | -------------------------------------------------- | -------------------------- |
| `WEB_REGISTRY_URL`        | full base URL of the web (scheme included)         | `http://localhost:8000`    |
| `GAME_PUBLIC_URL`         | this game's own reachable base URL (server → game) | `http://localhost:50055`   |
| `GAME_REGISTRATION_TOKEN` | shared token you request from an admin             | _(empty — required)_       |
| `REDIS_URL`               | Redis for persistence                              | `redis://localhost:6379/0` |

> In production the URLs are full https URLs (e.g. `https://<web>.up.railway.app`
> and `https://<your-game>.up.railway.app`).

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
./start.sh                 # HTTP server on 0.0.0.0:50055
```

Smoke test:

```bash
GID=$(curl -s -X POST localhost:50055/games -H 'Content-Type: application/json' \
  -d '{"players":["alice","bob"]}' | python -c 'import sys,json;print(json.load(sys.stdin)["game_id"])')
curl -s -X POST "localhost:50055/games/$GID/actions" -H 'Content-Type: application/json' \
  -d '{"game_data":{"action":"play","data":{"number":7}}}'
```

## Tests

```bash
python -m unittest discover -s tests
```

## Deploy

Any host that runs the `Dockerfile`/`Procfile` works (the platform uses
Railway). Set `WEB_REGISTRY_URL`, `GAME_PUBLIC_URL` and `REDIS_URL`, and the
game registers itself on boot.
