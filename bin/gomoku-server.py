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
        self.name = None
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
                self.update_ratings(result)
                if result == utils.colors.NONE:
                    for player in self.players.itervalues():
                        player.done(board, utils.results.DRAW)
                else:
                    # TODO: This seems broken, should be a better way of
                    # doing this
                    # TODO: This also should somehow merge with update_ratings,
                    # this seems to be in violation of DRY
                    self.players.pop(result).done(board, utils.results.VICTORY)
                    self.players.itervalues().next().done(board, utils.results.DEFEAT)
                break
        # Cleaning up
        self.opponent = None
        self.color = None
        self.state = READY


    def update_ratings(self, color):
        points = {self.color: 1.0, self.opponent.color: 0.0}.get(color, 0.5)
        mine = utils.loads(self.factory.db[self.name])
        others = utils.loads(self.factory.db[self.opponent.name])
        mine['rating'], others['rating'] = utils.elo(mine['rating'],
                                                     others['rating'],
                                                     points)
        self.factory.db[self.name] = utils.dumps(mine)
        self.factory.db[self.opponent.name] = utils.dumps(others)


    def done(self, board, result):
        """Called when the game has ended"""
        rating = int(utils.loads(self.factory.db[self.name])['rating'])
        self.send({'action': utils.play.DONE,
                   'board': board,
                   'result': result,
                   'rating': rating})


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
            user = str(request['user'])
            desc = utils.loads(self.factory.db[user])
            # TODO: maybe add check for human players trying to auth as bots?
            if desc['password'] == str(request['password']):
                self.state = AUTHENTICATED
                self.name = user
                self.send({'action': utils.auth.AUTH,
                           'rating': int(round(desc['rating']))})
            else:
                self.send({'action': utils.auth.BADPASSWORD})
        except KeyError:
            self.send({'action': utils.auth.USERNOTFOUND})


    def register(self, request):
        try:
            user = str(request['user'])
            if user in self.factory.db:
                # This is bad, we shouldn't allow someone overwriting already
                # existing users
                self.send({'action': utils.general.BADREQUEST})
            else:
                # TODO: Don't store plain-text passwords!
                self.factory.db[user] = utils.dumps(
                    {'password': request['password'],
                     'type': 'human',
                     'rating': 1500})
                self.state = AUTHENTICATED
                self.name = user
                self.send({'action': utils.auth.REGISTER,
                           'rating': 1500})
        except KeyError:
            self.send({'action': utils.general.BADREQUEST})


    def opponents(self, request):
        """Propose opponents for the player"""
        # We're currently using only AI bots, human players support will
        # get added later
        opponents = [{'name': name, 'rating': int(desc['rating']), 'type': 'AI'}
                     for name, desc in
                     ((name, utils.loads(desc)) for name, desc
                      in self.factory.db.iteritems())
                     if desc['type'] == 'AI']
        self.send({'action': utils.play.OPPONENTS,
                   'opponents': opponents})


class GomokuFactory(Factory):

    """Main server factory"""

    protocol = GomokuProtocol


    def __init__(self, dbpath):
        self.dbpath = dbpath
        self.db = None


    def startFactory(self):
        self.db = anydbm.open(self.dbpath, 'c')
        # Initialize db with bot
        if 'Herbie' not in self.db:
            self.db['Herbie'] = utils.dumps({'password': None,
                                             'type': 'AI',
                                             'engine': 'random_ai',
                                             'rating': 1500.0})


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
