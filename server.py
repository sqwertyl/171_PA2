import hashlib
import os
import threading
import time

from blockchain import Block, Node, Transaction


class Server(Node):
    def __init__(self):
        Node.__init__(self, 31337)
        self.BLOCKCHAIN = []

        threading.Thread(target=self.handle_user_input).start()

        for _ in range(3):
            conn, addr = self.SOCKET.accept()
            threading.Thread(target=self.handle_client,
                             args=(conn, addr)).start()
            self.conns.append(conn)

    def handle_user_input(self):
        while not self.exit_event.is_set():
            command = input().split(" ")
            if command[0] == "Balance":
                p1 = self.balance_request("P1")
                p2 = self.balance_request("P2")
                p3 = self.balance_request("P3")
                print(f"P1: ${p1}, P2: ${p2}, P3: ${p3}")
            elif command[0] == "Blockchain":
                print(f"[{', '.join(map(str, self.BLOCKCHAIN))}]")
            elif command[0] == "wait":
                time.sleep(int(command[1]))
            elif command[0] == "exit":
                self.exit_event.set()
                for conn in self.conns:
                    conn.close()
                self.SOCKET.close()
                break
        os._exit(0)

    def handle_client(self, conn, _):
        with conn:
            while not self.exit_event.is_set():
                data = conn.recv(1024)
                if data:
                    data = data.decode().split(" ")
                    if data[0] == "b":
                        out = self.balance_request(data[1])
                        conn.sendall(f"Balance: ${out}".encode())
                    elif data[0] == "t":
                        out = self.transfer_request(
                            data[1], data[2], int(data[3]))
                        conn.sendall(out.encode())
                else:
                    break

    def balance_request(self, address):
        balance = 10
        for block in self.BLOCKCHAIN:
            transaction = block.transaction
            if transaction.sender == address:
                balance -= transaction.amount
            if transaction.receiver == address:
                balance += transaction.amount
        return balance

    def transfer_request(self, sender, receiver, amount):
        if self.balance_request(sender) < amount:
            return "INCORRECT"

        last_block = "0" * 64 if len(self.BLOCKCHAIN) == 0 \
            else self.hash(self.BLOCKCHAIN[-1].hash_str())

        transaction = Transaction(sender, receiver, amount)
        nonce = self.calculate_nonce(transaction, last_block)
        block = Block(last_block, transaction, nonce)
        self.BLOCKCHAIN.append(block)
        return "SUCCESS"

    def calculate_nonce(self, transaction, last_block):
        nonce = 0
        while True:
            new_hash = self.hash(f"{last_block}{transaction}{nonce}")
            if int(new_hash[0], 16) <= 3:
                return nonce
            nonce += 1

    def hash(self, s):
        h = hashlib.sha256()
        s_bytes = s.encode()
        h.update(s_bytes)
        return h.hexdigest().zfill(64)


try:
    Server()
except Exception:
    pass