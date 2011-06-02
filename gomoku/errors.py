#!/usr/bin/env python



class NoMovePossible(Exception):
    """Raised when the move is impossible due to lack
    of empty cells or will break rules"""
    pass


class IllegalMove(Exception):
    """Raised when move attempted is considered illegal by the game rules"""
    pass


class Overwrite(IllegalMove):
    """Raised when move is attempted on the field already occupied"""
    pass


class DoubleThree(IllegalMove):
    """Raised when move violates 3x3 Renju rule"""
    pass


class DoubleFour(IllegalMove):
    """Raised when move violates 4x4 Renju rule"""
    pass


class Overline(IllegalMove):
    """Raised when there are 6 or more black stones in a row"""
    pass
