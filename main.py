from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from socket import socket
import datetime
import urllib.parse
import mimetypes
import json


UDP_IP = '127.0.0.1'
UDP_PORT = 5000
MESSAGE = "Python Web development"


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        else:
            if Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)
    
    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        run_udp_client(data=data)
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read()) 

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())


def run_http(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


def run_udp_server(ip, port):
    sock = socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    sock.bind(server)
    try:
        while True:
            data, address = sock.recvfrom(1024)
            print(f'Received data: {data.decode()} from: {address}')

            data_parse = urllib.parse.unquote_plus(data.decode())
            data_dict: dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
            with open("./storage/data.json", "wb") as file:
                json.dump({datetime.now(): data_dict}, file)
            sock.sendto(data, address)
            print(f'Send data: {data.decode()} to: {address}')
    except KeyboardInterrupt:
        print(f'Destroy server')
    finally:
        sock.close()


def run_udp_client(ip: str, port: int, data: str):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    sock.sendto(data, server)
    print(f'Send data: {data.decode()} to server: {server}')
    response, address = sock.recvfrom(1024)
    print(f'Response data: {response.decode()} from address: {address}')
    sock.close()

HTTPserver = Thread(target=run_http)
# UDPserver = Thread(target=run_udp, args=(UDP_IP, UDP_PORT))
# UDPclient = Thread(target=run_client, args=(UDP_IP, UDP_PORT))

if __name__ == '__main__':
    HTTPserver.start()
    # UDPserver.start()
    # UDPclient.start()