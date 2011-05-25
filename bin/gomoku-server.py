#!/usr/bin/env python

from __future__ import with_statement, print_function

"""
Server that runs gomoku game.

It should serve several purposes:
* Being able to connect two people for a game of gomoku
* Being able to connect to AI in case of player request (or in case he's the only player connected
* Tracking highscores (I assume using Elo rating system)
"""


import argparse
import random
from gomoku import utils
import anydbm
from twisted.internet import reactor
from twisted.internet.protocol import Factory
from twisted.protocols.basic import Int32StringReceiver
from twisted.internet.defer import (maybeDeferred, inlineCallbacks,
                                    returnValue, Deferred)


# just a set of constants which determine the state of the connection
CONNECTED = 0
DONE = -1
AUTHENTICATED = 1
PLAYING = 2
READY = 3



class GomokuProtocol(Int32StringReceiver):

    """Each client will have one of these"""


    factory = None


    def __init__(self):
        self.user = None
        self.state = CONNECTED
        self.color = None
        self.opponent = None
        self.colors = None
        self.deferred = None
        self.dispatch = {utils.auth.AUTH: self.auth,
                         utils.auth.REGISTER: self.register,
                         utils.play.OPPONENTS: self.opponents,
                         utils.play.INIT: self.play,
                         utils.play.MOVE: self.on_move}


    def send(self, response):
        response = utils.dumps(response)
        self.sendString(response)


    def stringReceived(self, string):
        request = utils.loads(string)
        try:
            self.dispatch[request['action']](request)
        except KeyError:
            self.send({'action': utils.general.NOTIMPLEMENTED})


    @inlineCallbacks
    def play(self, request):
        """Connect the player and his opponent (human or AI)

        Currently supports only AI."""
        colors = [utils.colors.BLACK, utils.colors.WHITE]
        if random.random() >= 0.5:
            colors.reverse()
        self.color = colors[0]
        self.opponent = utils.AIUser(request['opponent'], colors[1])
        self.players = {colors[0]: self, colors[1]: self.opponent}
        self.state = PLAYING
        board = utils.Board(15, 15)
        current = utils.colors.BLACK
        while True:
            player = self.players[current]
            board = yield maybeDeferred(player.move, board)
            result = board.done()
            if result is None:
                current = {utils.colors.BLACK: utils.colors.WHITE,
                           utils.colors.WHITE: utils.colors.BLACK}[current]
            else:
                if result == utils.colors.NONE:
                    for player in self.players.itervalues():
                        player.done(board, utils.results.DRAW)
                else:
                    # TODO: This seems broken, should be a better way of
                    # doing this
                    self.players.pop(result).done(board, utils.results.VICTORY)
                    self.players.itervalues().next().done(board, utils.results.DEFEAT)
                break
        self.state = READY


    def done(self, board, result):
        self.send({'action': utils.play.DONE,
                   'board': board,
                   'result': result})


    def move(self, board):
        self.deferred = Deferred()
        self.send({'action': utils.play.MOVE,
                   'board': board,
                   'color': self.color})
        return self.deferred


    def on_move(self, response):
        board = response['board']
        color = response['color']
        move = response['move']
        try:
            if board[move] is None:
                board[move] = self.color
                # Do something with callback, otherwise we might get double
                # callback issued, not good at all
                self.deferred.callback(board)
            else:
                self.send({'action': utils.play.OVERWRITE,
                           'board': board,
                           'color': self.color})
        except KeyError:
            self.send({'action': utils.play.OUTOFBOARD,
                       'board': board,
                       'color': self.color})


    def auth(self, request):
        try:
            if self.factory.db[str(request['user'])] == str(request['password']):
                self.state = AUTHENTICATED
                self.send({'action': utils.auth.AUTH})
            else:
                self.send({'action': utils.auth.BADPASSWORD})
        except KeyError:
            self.send({'action': utils.auth.NOTFOUND})


    def register(self, request):
        try:
            if str(request['user']) in self.factory.db:
                # This is bad, we shouldn't allow someone overwriting already
                # existing users
                self.send({'action': utils.general.BADREQUEST})
            else:
                self.factory.db[str(request['user'])] = str(request['password'])
                self.send({'action': utils.auth.REGISTER})
        except KeyError:
            self.send({'action': utils.general.BADREQUEST})


    def opponents(self, request):
        """Propose opponents for the player"""
        self.send({'action': utils.play.OPPONENTS,
                   'opponents': [{'name': 'Garry',
                                  'type': 'AI'},
                                 {'name': 'Bobby',
                                  'type': 'AI'}]})


class GomokuFactory(Factory):

    """Main server factory"""

    protocol = GomokuProtocol


    def __init__(self, dbpath):
        self.dbpath = dbpath
        self.db = None


    def startFactory(self):
        self.db = anydbm.open(self.dbpath, 'c')


    def stopFactory(self):
        self.db.close()



def main(args):
    factory = GomokuFactory(args.db_path)
    reactor.listenTCP(args.port, factory)
    reactor.run()



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', default=5672, type=int)
    parser.add_argument('-d', '--db-path', default='gomoku.db')
    main(parser.parse_args())
