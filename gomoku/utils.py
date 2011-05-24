#!/usr/bin/env python


from itertools import product



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
OPPONENTS = 10
PLAY = 11


def elo(first, second, result, kfactor=32):
    """Calculate the Elo rating based on player ratings and game result"""
    def expected(ratinga, ratingb):
        return 1.0 / (1 + 10**((ratingb - ratinga) / 400.0))
    return (first + kfactor * (result - expected(first, second)),
            second + kfactor * ((1.0 - result) - expected(second, first)))


def field():
    """Create empty field"""
    return dict.fromkeys(map(str, product(range(15), range(15))))


def find_neighbours(field):
    raise NotImplementedError




class AIUser(object):


    def __init__(self, name, color):
        self.name = name
        self.color = color


    def move(self, field):
