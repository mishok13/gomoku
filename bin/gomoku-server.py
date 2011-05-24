#!/usr/bin/env python

from __future__ import with_statement

"""
Server that runs gomoku game.

It should serve several purposes:
* Being able to connect two people for a game of gomoku
* Being able to connect to AI in case of player request (or in case he's the only player connected
* Tracking highscores (I assume using Elo rating system)
"""


import argparse
import simplejson
import random
from gomoku import utils
import anydbm
from twisted.internet import reactor
from twisted.internet.protocol import Factory
from twisted.protocols.basic import Int32StringReceiver


# just a set of constants which determine the state of the connection
CONNECTED = 0
DONE = -1
AUTHENTICATED = 1
PLAYING



class GomokuProtocol(Int32StringReceiver):

    """Each client will have one of these"""


    factory = None


    def __init__(self):
        self.user = None
        self.state = CONNECTED
        self.color = None
        self.dispatch = {utils.AUTH: self.auth,
                         utils.REGISTER: self.register,
                         utils.OPPONENTS: self.opponents,
                         utils.PLAY: self.play}


    def send(self, response):
        response = simplejson.dumps(response)
        self.sendString(response)


    def stringReceived(self, string):
        request = simplejson.loads(string)
        try:
            self.dispatch[request['action']](request)
        except KeyError:
            self.send({'action': utils.NOTIMPLEMENTED})


    def play(self, request):
        """Connect the player and his opponent (human or AI)"""
        if random.random() >= 0.5:
            self.color = 'black'
        else:
            self.color = 'white'
        field = utils.field()
        self.opponent = utils.AIUser(request['name'])



    def auth(self, request):
        try:
            if self.factory.db[str(request['user'])] == str(request['password']):
                self.state = AUTHENTICATED
                self.send({'action': utils.AUTH_OK})
            else:
                self.send({'action': utils.AUTH_ERR_PASSWORD})
        except KeyError:
            self.send({'action': utils.AUTH_ERR_NOTFOUND})


    def register(self, request):
        try:
            if str(request['user']) in self.factory.db:
                # This is bad, we shouldn't allow someone overwriting already
                # existing users
                self.send({'action': utils.BADREQUEST})
            else:
                self.factory.db[str(request['user'])] = str(request['password'])
                self.send({'action': utils.REG_OK})
        except KeyError:
            self.send({'action': utils.AUTH_ERR_NOTFOUND})


    def opponents(self, request):
        """Propose opponents for the player"""
        self.send({'action': utils.OPPONENTS,
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
