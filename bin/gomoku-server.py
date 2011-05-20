#!/usr/bin/env python

"""
Server that runs gomoku game.

It should serve several purposes:
* Being able to connect two people for a game of gomoku
* Being able to connect to AI in case of player request (or in case he's the only player connected
* Tracking highscores (I assume using Elo rating system)
"""


import argparse
import sys
import simplejson
from twisted.internet import reactor
from twisted.internet.protocol import Factory
from twisted.protocols.basic import Int32StringReceiver



class GomokuProtocol(Int32StringReceiver):

    """Each client will have one of these"""

    def stringReceived(self, string):
        string = simplejson.loads(string)



class GomokuFactory(Factory):

    """Main server factory"""

    protocol = GomokuProtocol




def main(args):
    factory = GomokuFactory()
    reactor.listenTCP(args.port, factory)
    reactor.run()



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', default=5672, type=int)
    main(parser.parse_args())
