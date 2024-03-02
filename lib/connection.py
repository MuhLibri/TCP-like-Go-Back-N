import socket
from .segment import Segment


# CONSTANTS
IP = "localhost"
PORT = 8000
BROADCAST_PORT = 9999
SEGMENT_SIZE = 32768
TIME_OUT = 5


class Connection:
    def __init__(self, ip = IP, port = PORT, broadcast_port = BROADCAST_PORT, is_client = True):
        self.ip = ip
        self.port = broadcast_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if is_client:
            self.client_port = port
            self.socket.bind((ip, port))
            print(f"[!] Client started at {self.ip}:{self.client_port}")
        else:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((ip, broadcast_port))
            print(f"[!] Server started at {self.ip}:{self.port}")

    def send(self, msg, dest):
        self.socket.sendto(msg, dest)

    def listen(self, time_out=0):
        try:
            if (time_out != 0):
                self.socket.settimeout(time_out)
            return self.socket.recvfrom(SEGMENT_SIZE)
        except TimeoutError as e:
            raise e

    def close(self):
        self.socket.close()