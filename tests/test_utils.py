#!/usr/bin/env python


import nose
from gomoku import utils
from itertools import product


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
    board = utils.Board(15, 15)
    assert board.done() is None
    board[(0, 0)] = utils.colors.BLACK
    assert board.done() is None
    board = utils.Board(15, 15)
    board.board = dict.fromkeys(product(range(15), range(15)), utils.colors.BLACK)
    assert board.done() == utils.colors.BLACK
    board = utils.Board(15, 15)
    for coord in [(x, 0) for x in xrange(5)]:
        board[coord] = utils.colors.BLACK
    assert board.done() == utils.colors.BLACK
    board = utils.Board(15, 15)
    for coord in [(0, y) for y in xrange(5)]:
        board[coord] = utils.colors.BLACK
    assert board.done() == utils.colors.BLACK
    board = utils.Board(15, 15)
    for coord in [(x, x) for x in xrange(5)]:
        board[coord] = utils.colors.BLACK
    assert board.done() == utils.colors.BLACK
    board = utils.Board(15, 15)
    for coord in [(x, y) for x, y in zip(xrange(5), xrange(4, -1, -1))]:
        board[coord] = utils.colors.BLACK
    assert board.done() == utils.colors.BLACK
