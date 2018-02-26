import re
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

from .config import config
from . import web_services


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
  timeout = config['wait_for_incoming_request_timeout']


class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        return self.do_XXX()

    def do_POST(self):
        return self.do_XXX()
  
    def do_XXX(self):
        for urlmap in config['urlmap']:
            cmd_pattern, url_pattern, handler_name = urlmap

            if re.search(cmd_pattern, self.command) and re.search(url_pattern, self.path):
                return getattr(web_services, handler_name)(self)

        self.send_response(404)
