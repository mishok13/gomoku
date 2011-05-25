#!/usr/bin/env python



class NoMovePossible(Exception):
    """Raised when the move is impossible due to lack
    of empty cells or will break rules"""
    pass
