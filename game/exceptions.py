class PunishableError(Exception):
    """Errors caused by the player's move -> they cost the player a penalty."""
    pass


class InvalidData(PunishableError):
    pass


class IllegalMoveException(PunishableError):
    pass


class InvalidActionError(PunishableError):
    pass


class NonPunishableError(Exception):
    """Errors not attributable to the player's move."""
    pass


class InvalidQuantityPlayers(NonPunishableError):
    pass


class GameNotFoundInRedis(Exception):
    pass
