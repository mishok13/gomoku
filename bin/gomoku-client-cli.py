#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple command-line Gomoku client
"""


from __future__ import print_function



import argparse
import simplejson
from gomoku import utils
from twisted.internet import reactor
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.basic import Int32StringReceiver



INITED = 0
AUTHENTICATED = 1



class GomokuClientProtocol(Int32StringReceiver):


    factory = None


    def __init__(self):
        self.dispatch = {utils.auth.AUTH: self.authenticated,
                         utils.auth.REGISTER: self.registered,
                         utils.auth.BADPASSWORD: self.wrongpass,
                         utils.auth.USERNOTFOUND: self.notauser,
                         utils.play.OPPONENTS: self.opponents,
                         utils.play.MOVE: self.on_move,
                         utils.play.OVERWRITE: self.on_move_overwrite,
                         utils.play.OUTOFBOARD: self.on_move_outofboard}


    def connectionMade(self):
        if self.factory.state != AUTHENTICATED:
            self.auth()


    def authenticated(self, response):
        """Callback issued when user has been authenticated"""
        self.factory.state = AUTHENTICATED
        self.send({'action': utils.play.OPPONENTS})


    def on_move_overwrite(self, request):
        print('You may not overwrite existing moves')
        self.on_move(request)


    def on_move_outofboard(self, request):
        print('Pieces should be placed on the board')
        self.on_move(request)


    def on_move(self, request):
        field = request['field']
        color = request['color']
        self.print_field(field)
        while True:
            move = raw_input("Print your move: ")
            if move:
                x, y = ord(move[0]) - 65, int(move[1:])
                break
        self.send({'action': utils.play.MOVE,
                   'color': color,
                   'field': field,
                   'move': (x, y)})



    def print_field(self, field):
        # TODO: Probably move it to function
        print(' ' * 3, ''.join(map('{:>3}'.format, xrange(15))), sep='')
        for x in xrange(15):
            print('{:>3} '.format(chr(x + 65)), end='')
            for y in xrange(15):
                piece = {utils.colors.BLACK: ' B ',
                         utils.colors.WHITE: ' W '}.get(field[(x, y)], u' · ')
                print(piece, end='')
            print()



    def registered(self, response):
        """Callback issued when user has been registered"""
        print('You have been registered!')
        self.authenticated(response)


    def wrongpass(self, response):
        print('Password mismatch!')
        self.auth()


    def opponents(self, response):
        print('There are following users:')
        opponents = list(enumerate(response['opponents']))
        for index, opponent in opponents:
            print('{}) {} ({})'.format(index,
                                       opponent['name'],
                                       opponent['type']))
        while True:
            selection = raw_input('Select opponent: ')
            if selection:
                selection = int(selection)
                if 0 <= selection < len(opponents):
                    break
        opponent = opponents[selection][1]
        self.send({'action': utils.play.INIT,
                   'opponent': opponent['name'],
                   'type': opponent['type']})


    def notauser(self, response):
        print('There is no such user. Registration required')
        while True:
            password = self.password()
            if password == self.password('Re-type your password: '):
                break
            print('Oops, the two password have to match. Try again')
        self.send({'action': utils.auth.REGISTER,
                   'user': self.factory.user,
                   'password': password})



    def password(self, message="Type your password: "):
        password = None
        while not password:
            password = raw_input(message)
        return password


    def auth(self):
        password = self.password()
        self.send({'action': utils.auth.AUTH,
                   'user': self.factory.user,
                   'password': password})


    def stringReceived(self, response):
        response = utils.loads(response)
        self.dispatch[response['action']](response)


    def send(self, request):
        request = utils.dumps(request)
        self.sendString(request)



class GomokuClientFactory(ReconnectingClientFactory):


    protocol = GomokuClientProtocol


    def __init__(self):
        self.state = INITED
        self.user = None


    def startFactory(self):
        while not self.user:
            self.user = raw_input('Name: ')


def main(args):
    factory = GomokuClientFactory()
    reactor.connectTCP(args.host, args.port, factory)
    reactor.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host', default='localhost', type=str)
    parser.add_argument('-p', '--port', default=5672, type=int)
    main(parser.parse_args())
