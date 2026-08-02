import os


def load_env_var(name: str, vartype: type = str, default: str = None):
    var = os.environ.get(name, default)
    if vartype == bool and str(var).lower() in ('0', 'false', ''):
        var = False
    if var is None:
        raise EnvironmentError(f'Missing required env var: {name}')
    return vartype(var)


# Redis (game persistence).
REDIS_URL = load_env_var('REDIS_URL', str, 'redis://:@localhost:6379/0')
DB = load_env_var('REDIS_DB_INDEX', int, '0')
DECODE_RESPONSES = load_env_var('DECODE_RESPONSES', bool, 'True')

# Self-registration with the web.
#   WEB_REGISTRY_URL  full base URL of the web (scheme included), e.g.
#                     http://localhost:8000 or https://<app>.up.railway.app
#   GAME_PUBLIC_URL   this game's own reachable base URL (what the server calls)
WEB_REGISTRY_URL = load_env_var('WEB_REGISTRY_URL', str, 'http://localhost:8000')
GAME_PUBLIC_URL = load_env_var('GAME_PUBLIC_URL', str, 'http://localhost:50055')
