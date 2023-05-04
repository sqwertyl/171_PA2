import socket
import threading


class Block:
    def __init__(self, hp, t, n):
        self.hash_pointer = hp
        self.transaction = t
        self.nonce = n

    def hash_str(self):
        return f"{self.hash_pointer}{self.transaction}{self.nonce}"

    def __str__(self):
        return f"({self.transaction.sender}, {self.transaction.receiver}, ${self.transaction.amount}, {self.hash_pointer})"


class Transaction:
    def __init__(self, s, r, a):
        self.sender = s
        self.receiver = r
        self.amount = a

    def __str__(self):
        return f"{self.sender}{self.receiver}${self.amount}"


class Node:
    def __init__(self, port):
        self.HOST = "localhost"
        self.PORT = port
        self.SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.SOCKET.bind((self.HOST, self.PORT))
        self.SOCKET.listen(4)
        self.exit_event = threading.Event()
        self.conns = []


class Timestamp:
    def __init__(self, msg):
        msg = msg.split(" ")
        self.ts = int(msg[1])
        self.port = int(msg[2])

    def __lt__(self, other):
        return self.ts < other.ts or (self.ts == other.ts and self.port < other.port)

    def __eq__(self, other):
        return self.ts == other.ts and self.port == other.port

    def __gt__(self, other):
        return self.ts > other.ts or (self.ts == other.ts and self.port > other.port)