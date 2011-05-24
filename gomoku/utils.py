#!/usr/bin/env python


# Actions clients can send
AUTH = 0
REGISTER = 1
MOVE = 2
BADREQUEST = 3

# Actions server can send
AUTH_OK = 4
AUTH_ERR_NOTFOUND = 5
AUTH_ERR_PASSWORD = 6
REG_OK = 7
NOTIMPLEMENTED = 8
FIELD = 9


def elo(first, second, result, kfactor=32):
    """Calculate the Elo rating based on player ratings and game result"""
    def expected(ratinga, ratingb):
        return 1.0 / (1 + 10**((ratingb - ratinga) / 400.0))
    return (first + kfactor * (result - expected(first, second)),
            second + kfactor * ((1.0 - result) - expected(second, first)))
