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
        self.dispatch = {utils.auth.AUTH: self.on_auth,
                         utils.auth.REGISTER: self.on_register,
                         utils.auth.BADPASSWORD: self.err_wrongpass,
                         utils.auth.USERNOTFOUND: self.err_notauser,
                         utils.play.OPPONENTS: self.opponents,
                         utils.play.MOVE: self.on_move,
                         utils.play.OVERWRITE: self.err_overwrite,
                         utils.play.OUTOFBOARD: self.err_outofboard,
                         utils.play.DONE: self.on_game_done}


    def connectionMade(self):
        if self.factory.state != AUTHENTICATED:
            self.auth()


    def on_auth(self, response):
        """Callback issued when user has been authenticated"""
        self.factory.state = AUTHENTICATED
        print('Your rating is: {}'.format(response['rating']))
        self.send({'action': utils.play.OPPONENTS})


    def err_overwrite(self, request):
        print('You may not overwrite existing moves')
        self.on_move(request)


    def err_outofboard(self, request):
        print('Pieces should be placed on the board')
        self.on_move(request)


    def on_move(self, request):
        board = request['board']
        color = request['color']
        board.show()
        while True:
            move = raw_input("Print your move: ")
            if move:
                x, y = ord(move[0]) - 65, int(move[1:])
                break
        self.send({'action': utils.play.MOVE,
                   'color': color,
                   'board': board,
                   'move': (x, y)})


    def on_game_done(self, request):
        result = request['result']
        result = {utils.results.VICTORY: "won",
                  utils.results.DRAW: "drawn",
                  utils.results.DEFEAT: "lost"}[result]
        print('You {}. Your rating is now {}.'.format(result,
                                                      request['rating']))
        while True:
            answer = raw_input("Do you want to play once more? [y/N] ")
            if answer == 'y':
                self.send({'action': utils.play.OPPONENTS})
                break
            elif answer == 'N':
                reactor.stop()
                break
            else:
                print('Please answer "y" or "N". ', end='')


    def on_register(self, response):
        """Callback issued when user has been registered"""
        print('You have been registered!')
        self.on_auth(response)


    def err_wrongpass(self, response):
        print('Password mismatch!')
        self.auth()


    def opponents(self, response):
        print('There are following users:')
        opponents = list(enumerate(response['opponents']))
        for index, opponent in opponents:
            print('{}) {} ({}) with rating of {}'.format(index,
                                                         opponent['name'],
                                                         opponent['type'],
                                                         opponent['rating']))
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


    def err_notauser(self, response):
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
