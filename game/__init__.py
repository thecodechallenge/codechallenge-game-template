# =====================================================================
# TODO: rename your game here. `NAME` is the identifier the server routes
# by (a slug); DISPLAY_NAME and DESCRIPTION are shown in the web.
# =====================================================================
GAME_NAME = 'my-game'
GAME_DISPLAY_NAME = 'My Game'
GAME_DESCRIPTION = (
    'A template game. Replace this description with how your game is played.'
)

# States reported back to the server (leave as-is).
VALID_STATE = 'valid'
INVALID_STATE = 'invalid'
GAMEOVER_STATE = 'gameover'
ABORT = 'game aborted'
TIMEOUT = 'timeout'
STATE = 'state'

# Turn / player identifiers (the two seats). Leave as-is.
SIDE = ['A', 'B']

# =====================================================================
# TODO: tune your game constants.
# =====================================================================
TOTAL_MOVES = 20          # turns before the game ends by move count
EMPTY = ''

# Action protocol from the client: {"action": ..., "data": {...}}.
ACTION = 'action'
DATA = 'data'
# TODO: name your action(s) and the keys inside `data`.
PLAY_ACTION = 'play'
NUMBER = 'number'

# Scores. TODO: tune to your game.
SCORE_PENALTY = -5
SCORE_FORCE_GAMEOVER = SCORE_PENALTY * 5

# Echoed back in play_data when a turn is skipped by timeout.
INVALID_PENALIZE = {NUMBER: 'invalid'}
