#!/usr/bin/env python


import nose
from gomoku import utils


def test_elo():
    rating = 1613
    for opponent, result in [(1609, 0.0),
                             (1477, 0.5),
                             (1388, 1.0),
                             (1586, 1.0),
                             (1720, 0.0)]:
        rating = utils.elo(rating, opponent, result)[0]
        print rating
