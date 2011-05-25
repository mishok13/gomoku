#!/usr/bin/env python


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
colors = Constants()
colors.BLACK = 500
colors.WHITE = 501
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
    return dict.fromkeys(product(range(15), range(15)))



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



def done(field):
    """Check if the field has winning/draw situation"""
    return all(field.itervalues())
