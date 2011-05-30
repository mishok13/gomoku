#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

from itertools import product
import cPickle as pickle
import random
from gomoku import errors



class Constants(object): pass


#pylint: disable-msg=w0201
general = Constants()
general.NOTIMPLEMENTED = 0
general.BADREQUEST = 1
auth = Constants()
auth.AUTH = 100
auth.REGISTER = 101
auth.USERNOTFOUND = 102
auth.BADPASSWORD = 103
play = Constants()
play.INIT = 400
play.MOVE = 401
play.OPPONENTS = 402
play.OVERWRITE = 403
play.OUTOFBOARD = 404
play.DONE = 405
colors = Constants()
colors.BLACK = 500
colors.WHITE = 501
colors.NONE = 502
results = Constants()
results.VICTORY = 600
results.DRAW = 601
results.DEFEAT = 602
#pylint: enable-msg=w0201


# Both these functions have been put here to make future changes
# to different serialization methods easier

def dumps(data):
    """Serializing data"""
    return pickle.dumps(data)



def loads(data):
    """De-serializing data"""
    return pickle.loads(data)



def elo(first, second, result, kfactor=32):
    """Calculate the Elo rating based on player ratings and game result"""
    def expected(ratinga, ratingb):
        return 1.0 / (1 + 10**((ratingb - ratinga) / 400.0))
    return (first + kfactor * (result - expected(first, second)),
            second + kfactor * ((1.0 - result) - expected(second, first)))



def field():
    """Create empty field"""
    return Board(15, 15)



def empty_neighbours(field):
    # TODO: I think there's a room for improvement
    # Even more, this is fricking ugly
    for key, value in field.iteritems():
        if value is not None:
            for x in xrange(key[0] - 1, key[0] + 2):
                for y in xrange(key[1] - 1, key[1] + 2):
                    try:
                        if field[(x, y)] is None:
                            yield (x, y)
                    except KeyError:
                        continue



class AIUser(object):

    """Dummy implementation of AI.

    The implementation does its best at not doing any actual AI.
    The principle is following -- put the piece on the field that
    has occupied neighbour. That's it. I suck at AI."""


    def __init__(self, name, color):
        self.name = name
        self.color = color


    def move(self, field):
        """Make stupid move by randomly choosing from unoccupied neighbours.

        This would even work for empty fields.
        """
        neighbours = list(set(empty_neighbours(field)))
        if neighbours:
            field[random.choice(neighbours)] = self.color
        else:
            if any(field[coord] for coord in neighbours):
                # If we have non-empty celss, then we're probably out of possible moves
                raise errors.NoMovePossible
            else:
                field[random.choice(field.keys())] = self.color
        return field


    def done(self, *_):
        """Dummy method"""
        pass



class Board(object):


    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = dict.fromkeys(product(xrange(width), xrange(height)))
        self.actions = []


    def __getitem__(self, coord):
        return self.board[coord]


    def __setitem__(self, coord, color):
        if color not in (colors.WHITE, colors.BLACK):
            raise ValueError('Only white and black pieces are allowed')
        self.board[coord] = color
        self.actions.append(('MOVE', coord, color))
        #TODO: add aditional checks for Renju


    def itervalues(self):
        return self.board.itervalues()


    def iteritems(self):
        return self.board.iteritems()


    def get(self, coord, default=None):
        return self.board.get(coord, default)


    def keys(self):
        return self.board.keys()


    def done(self, length=5):
        """Check if the field has winning/draw situation"""
        # This should probably go into decorator, but having only
        # one use-case, it would a bit strange
        result = self._done(length)
        if result is not None:
            self.actions.append(('STOP', (-1, -1), result))
        return result


    def _done(self, length):
        # This algorithm runs in O(m * n * k) time, I wonder
        # if there's room for improvement
        for coord, color in self.iteritems():
            if color is None:
                continue
            if all(self.get((coord[0], y)) == color
                   for y in xrange(coord[1], coord[1] + length)):
                return color
            if all(self.get((x, coord[1])) == color
                   for x in xrange(coord[0], coord[0] + length)):
                return color
            if all(self.get((x, x)) == color
                   for x in xrange(coord[0], coord[0] + length)):
                return color
            if all(self.get((x, y)) == color
                   for x, y in zip(xrange(coord[0], coord[0] + length),
                                   xrange(coord[1], coord[1] - length, -1))):
                return color
        if all(self.itervalues()):
            # We have nothing else to put here, so it's a draw
            return colors.NONE
        return None


    def show(self):
        # TODO: Probably move it to function
        print(' ' * 3, ''.join(map('{:>3}'.format, xrange(15))), sep='')
        for x in xrange(15):
            print('{:>3} '.format(chr(x + 65)), end='')
            for y in xrange(15):
                piece = {colors.BLACK: ' B ',
                         colors.WHITE: ' W '}.get(self[(x, y)], u' · ')
                print(piece, end='')
            print()
