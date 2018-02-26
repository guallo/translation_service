#!/usr/bin/python

import os
import sys
import signal

LIB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'lib'))
sys.path.append(LIB_DIR)

from translation_service import config
from translation_service import hooks
from translation_service import http_server

LISTEN = ('localhost', 8080)


def sigint_handler(signal, frame):
    global serve_request
    serve_request = False


httpd = http_server.ThreadingHTTPServer(LISTEN, http_server.HTTPRequestHandler)

for hook_name in config.config['on_server_start']:
    hook = getattr(hooks, hook_name)
    hook()

serve_request = True
signal.signal(signal.SIGINT, sigint_handler)

print 'Entering main loop...'

while serve_request:
    httpd.handle_request()

print 'Finished main loop'

for hook_name in config.config['on_server_stop']:
    hook = getattr(hooks, hook_name)
    hook()

httpd.server_close()
