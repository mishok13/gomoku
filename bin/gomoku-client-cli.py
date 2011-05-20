#!/usr/bin/env python


"""
Simple command-line client
"""


from __future__ import print_function



import argparse
import socket
import simplejson
import struct



HEADER = struct.calcsize('!I')



def read(sock):
    header = sock.recv(HEADER)
    length = struct.unpack('!I', header)[0]
    body = sock.recv(length)
    return simplejson.loads(body)



def write(sock, data):
    body = simplejson.dumps(data)
    length = len(body)
    header = struct.pack('!I', length)
    sock.send(header + body)



def greet(sock):
    name = raw_input("Type in your name: ")
    write(sock, {'action': 'greet', 'name': name})
    return read(sock)



def main(args):
    sock = socket.create_connection((args.host, args.port))
    greet(sock)
    while True:
        act(read(sock))
        move(sock)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host', default='localhost', type=str)
    parser.add_argument('-p', '--port', default=5672, type=int)
    main(parser.parse_args())
