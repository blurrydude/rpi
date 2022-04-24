# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO
import time

class SmarterCircuitsWeb:
    def __init__(self, hostName, port):
        self.webServer = HTTPServer((hostName, port), WebServer)
    
    def start(self):
        self.webServer.serve_forever()

    def stop(self):
        self.webServer.server_close()

class WebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>Smarter Circuits</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        response = BytesIO()
        response.write(b'This is POST request. ')
        response.write(b'Received: ')
        response.write(body)
        response_value = response.getvalue()
        print(response)
        self.wfile.write(response_value)
