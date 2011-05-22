#!/usr/bin/env python


"""
Simple command-line client
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
        self.dispatch = {utils.AUTH_OK: self.authenticated,
                         utils.REG_OK: self.registered,
                         utils.AUTH_ERR_PASSWORD: self.wrongpass,
                         utils.AUTH_ERR_NOTFOUND: self.notauser}


    def connectionMade(self):
        if self.factory.state != AUTHENTICATED:
            self.auth()


    def authenticated(self, response):
        self.factory.state = AUTHENTICATED


    def registered(self, response):
        print('You have been registered!')
        self.factory.state = AUTHENTICATED


    def wrongpass(self, response):
        print('Password mismatch!')
        self.auth()


    def notauser(self, response):
        print('There is no such user. Registration required')
        while True:
            password = self.password()
            if password == self.password('Re-type your password: '):
                break
            print('Oops, the two password have to match. Try again')
        self.send({'action': utils.REGISTER,
                   'user': self.factory.user,
                   'password': password})



    def password(self, message="Type your password: "):
        password = None
        while not password:
            password = raw_input(message)
        return password


    def auth(self):
        password = self.password()
        self.send({'action': utils.AUTH,
                   'user': self.factory.user,
                   'password': password})


    def stringReceived(self, response):
        response = simplejson.loads(response)
        self.dispatch[response['action']](response)


    def send(self, request):
        request = simplejson.dumps(request)
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
