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



def test_done():
    field = utils.field()
    assert utils.done(field) != True
    field[(0, 0)] = utils.colors.BLACK
    assert utils.done(field) != True
    assert utils.done(dict.fromkeys(field.iterkeys(), utils.colors.BLACK)) == True
    field = utils.field()
    for coord in [(x, 0) for x in xrange(5)]:
        field[coord] = utils.colors.BLACK
    assert utils.done(field) == True
    field = utils.field()
    for coord in [(0, y) for y in xrange(5)]:
        field[coord] = utils.colors.BLACK
    assert utils.done(field) == True
    field = utils.field()
    for coord in [(x, x) for x in xrange(5)]:
        field[coord] = utils.colors.BLACK
    assert utils.done(field) == True
    field = utils.field()
    for coord in [(x, y) for x, y in zip(xrange(5), xrange(4, -1, -1))]:
        field[coord] = utils.colors.BLACK
    assert utils.done(field) == True
