import socket
from threading import Thread
from typing import Tuple, Literal

ADDRESS = Tuple[str, int]

def parse_request(request):
    lines = request.split("\r\n")
    method, path, protocol = lines[0].split(" ")
    return method, path

class HTTPCore(socket.socket):
    def __init__(self):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind(("127.0.0.1", 8000))

    def handle_request(self, connection: socket.socket, address: ADDRESS):
        request = connection.recv(1024).decode()
        
        # Parse the request to extract method and path
        method, path = parse_request(request)
        
        # Print the requested URL
        print("Requested URL:", path)
        self.send_message(connection, "<h1>YESSSSSSSSSSSSSSSSSSSSSS</h1>")

    def start(self):
        self.listen()
        print("Running")
        while True:
            _conn, _addr = self.accept()
            thread = Thread(target=self.handle_request, args=(_conn, _addr))
            thread.start()
            

    def send_message(self, connection: socket.socket, 
                     message: str, 
                     status_code: int = 200,
                     status_message: str = "OK") -> Literal[True] | None:
        response = f"HTTP/1.1 {status_code} {status_message}\nContent-Type: text/html\n\n" + message
        connection.send(response.encode())
        connection.close()

core = HTTPCore()
core.start()