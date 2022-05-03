#!/usr/bin/env python

from http.server import HTTPServer, BaseHTTPRequestHandler

import logging
import ssl
import argparse
import os.path

logging.basicConfig(level=logging.DEBUG)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser(description="Simple server that logs all request details")
parser.add_argument('--port', type=int, default=443, help='Listening port')
# You can generate a self-signed certificate pair using
# openssl req -x509 -nodes -days 365 -newkey rsa:4096 -keyout mitm.key -out mitm.crt
parser.add_argument('--cert', default=os.path.join(SCRIPT_DIR, "certs", "mitm.crt"), help='Certificate file path')
parser.add_argument('--key', default=os.path.join(SCRIPT_DIR, "certs", "mitm.key"), help='Key file path')

args = parser.parse_args()


class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self, method="POST"):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        logging.info(f"{method} request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                     str(self.path), str(self.headers), post_data.decode('utf-8'))

        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

    def do_PATCH(self):
        self.do_POST("PATCH")


httpd = HTTPServer(('0.0.0.0', args.port), S)

httpd.socket = ssl.wrap_socket(httpd.socket,
                               keyfile=args.key,
                               certfile=args.cert,
                               server_side=True)
httpd.serve_forever()
