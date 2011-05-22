#!/usr/bin/env python


# Actions clients can send
AUTH = 0
REGISTER = 1
MOVE = 2
BADREQUEST = 3

# Actions server can send
AUTH_OK = 4
AUTH_ERR_NOTFOUND = 5
AUTH_ERR_PASSWORD = 6
REG_OK = 7
NOTIMPLEMENTED = 8
