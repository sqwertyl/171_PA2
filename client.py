import heapq
import os
import socket
import sys
import threading
import time

from blockchain import Node, Timestamp


class Client(Node):
    def __init__(self):
        self.ADDR = sys.argv[1]
        self.SERVER_PORT = 31337
        Node.__init__(self, self.SERVER_PORT + int(self.ADDR[1]))

        self.SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SERVER_SOCKET.connect((self.HOST, self.SERVER_PORT))

        threading.Thread(target=self.handle_server_response).start()
        threading.Thread(target=self.handle_user_input).start()

        threading.Thread(target=self.handle_lamport).start()
        threading.Thread(target=self.handle_lamport).start()

        self.timestamp = 0
        self.peers = {}
        self.request_queue = []
        self.transfer_queue = []
        self.received_replies = {}
        clients = set([31338, 31339, 31340])
        clients.remove(self.PORT)

        time.sleep(5)

        for client in clients:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.HOST, client))
            self.peers[client] = s
            self.received_replies[client] = 0

    def handle_user_input(self):
        while not self.exit_event.is_set():
            command = input().split(" ")
            if command[0] == "Balance":
                self.update_lamport_clock("Local")
                self.SERVER_SOCKET.sendall(f"b {self.ADDR}".encode())
            elif command[0] == "Transfer":
                self.update_lamport_clock("Send")
                request = f"REQUEST {self.timestamp} {self.PORT}"
                for peer in self.peers:
                    self.peers[peer].sendall(request.encode())
                    time.sleep(0.5)
                heapq.heappush(self.request_queue, Timestamp(request))
                self.transfer_queue.append(
                    f"t {self.ADDR} {command[1]} {command[2][1:]}")
                print(request[:-6])
            elif command[0] == "wait":
                time.sleep(int(command[1]))
            elif command[0] == "exit":
                self.exit_event.set()
                self.SERVER_SOCKET.close()
                break
        os._exit(0)

    def handle_server_response(self):
        while not self.exit_event.is_set():
            data = self.SERVER_SOCKET.recv(1024)
            time.sleep(3)
            if data:
                data = data.decode()
                if data == "SUCCESS" or data == "INCORRECT":
                    heapq.heappop(self.request_queue)
                    self.update_lamport_clock("Send")
                    for peer in self.peers:
                        self.peers[peer].sendall(
                            f"RELEASE {self.timestamp} {self.PORT}".encode())
                    print(f"RELEASE {self.timestamp}")
                print(data)
            else:
                break

    def handle_lamport(self):
        conn, _ = self.SOCKET.accept()
        self.conns.append(conn)
        while not self.exit_event.is_set():
            data = conn.recv(1024)
            time.sleep(3)
            if data:
                data = data.decode().split(" ")
                if data[0] == "REQUEST":
                    self.peers[int(data[2])].sendall(
                        f"REPLY {self.timestamp} {self.PORT}".encode())
                    heapq.heappush(self.request_queue,
                                   Timestamp(" ".join(data)))
                    print(f"REPLY {data[1]}")
                elif data[0] == "REPLY":
                    self.received_replies[int(data[2])] += 1
                    if self.request_queue and heapq.nsmallest(1, self.request_queue)[0].port == self.PORT and self.check_replies():
                        self.consume_replies()
                        self.SERVER_SOCKET.sendall(
                            self.transfer_queue.pop(0).encode())
                    print(f"REPLIED {data[1]}")
                elif data[0] == "RELEASE":
                    heapq.heappop(self.request_queue)
                    print("DONE")
                self.update_lamport_clock("Receive", int(data[1]))
            else:
                break

    def check_replies(self):
        for reply in self.received_replies:
            if self.received_replies[reply] <= 0:
                return False
        return True

    def consume_replies(self):
        for reply in self.received_replies:
            self.received_replies[reply] -= 1

    def update_lamport_clock(self, event_type, incoming_timestamp=-1):
        if event_type != "Receive":
            print(
                f"{event_type} Event, Incrementing TS, New TS: {self.timestamp + 1}")
            self.timestamp += 1
        else:
            new_timestamp = max(self.timestamp, incoming_timestamp) + 1
            print(
                f"{event_type} Event, Local TS: {self.timestamp}, Incoming TS: {incoming_timestamp}, New TS: {new_timestamp}")
            self.timestamp = new_timestamp


try:
    Client()
except Exception:
    pass