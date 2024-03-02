import lib.connection as conn
import lib.segment as seg
from lib.parser import Parser
from socket import timeout as socket_timeout
import os
import math
import sys

WINDOW = 3


class Server:
    def __init__(self):
        args = Parser(is_client=False)
        broadcast_port, pathfile_input = args.get_values()

        if not os.path.exists(f"in/{pathfile_input}"):
            print(f"The file in/{pathfile_input} does not exist.")
            sys.exit(1)

        self.ip = conn.IP
        self.port = broadcast_port
        self.pathfile_input = pathfile_input
        self.segment = seg.Segment()
        self.client_list = []
        self.connection = conn.Connection(is_client=False, broadcast_port=broadcast_port)

    def three_way_handshake(self, data, addr):
        print("[!] Initiating three way handshake...")
        print("[!] Waiting for request...")

        try:
            # Lsitening for SYN
            self.segment.set_segment_bytes(data)
            flag = self.segment.get_flag()
            if (flag.is_syn()):
                print(f"[!] [Handshake] Received SYN request from client {addr[0]}:{addr[1]}")
                print(f"    flag: SYN   seq_num: {self.segment.get_seq_num()}   ack_num: {self.segment.get_ack_num()}")
                self.segment.set_flag(["SYN", "ACK"])
                self.segment.set_ack_num(self.segment.seq_num + 1)
                self.segment.set_seq_num(0)
                self.connection.send(self.segment.get_segment_bytes(), addr)
                print(f"[!] [Handshake] SYN ACK request sent to client {addr[0]}:{addr[1]}")
                print(f"    flag: SYN ACK   seq_num: {self.segment.get_seq_num()}   ack_num: {self.segment.get_ack_num()}")            

            data, addr = self.connection.listen()
            self.segment.set_segment_bytes(data)
            flag = self.segment.get_flag()
            if (flag.is_ack()):
                print(f"[!] [Handshake] Received ACK request from client {addr[0]}:{addr[1]}")
                print(f"    flag: ACK  seq_num: {self.segment.get_seq_num()}   ack_num: {self.segment.get_ack_num()}")
                print("[!] [Handshake] Connection Established")
                return True
            else:
                return False
        except socket_timeout:
            print("[ERR] [Handshake] Timed out")
            return False

    def listen_broadcast(self):
        fileSize = os.path.getsize(f"in/{self.pathfile_input}")
        print(f"[!] Source file | {self.pathfile_input} | {fileSize} bytes")
        print("[!] Listening to broadcast address for clients\n")
        listening = True

        while listening:
            try:
                data, addr = self.connection.listen()
                print(f"[!] Received request from {addr[0]}:{addr[1]}")
                if((data, addr) not in self.client_list):
                    self.client_list.append((data, addr))
                listening = input("[?] Listen more? (y/n) ") == "y"
                print("\nClient list:")
                for i in range (len(self.client_list)):
                    print(f"{i+1}. {self.client_list[i][1][0]}:{self.client_list[i][1][1]}")
                print()
            except socket_timeout:
                print("[ERR] Timed out")
    
    def run(self):
        while len(self.client_list) > 0:
            client = self.client_list[0]
            segment = seg.Segment()
            segment.set_segment_bytes(client[0])
            self.client_list.remove(client)
            if segment.get_payload().decode("utf-8") == "tictactoe":
                print(f"[Client {client[1][0]}:{client[1][1]}] Tic Tac Toe")
                isShaked = self.three_way_handshake(client[0], client[1])
                found = False
                for client2 in self.client_list:
                    segment2 = seg.Segment()
                    segment2.set_segment_bytes(client2[0])
                    if segment2.get_payload().decode("utf-8") == "tictactoe":
                        found = True
                        self.client_list.remove(client2)
                        break
                if found:
                    if(isShaked and self.three_way_handshake(client2[0], client2[1])):
                        self.tictactoe((client[1], client2[1]))
                else:
                    print(f"[!] Sending message opponent not found to client")
                    segmentNotFound = seg.Segment()
                    segmentNotFound.set_flag(["FIN"])
                    segmentNotFound.set_payload(b"Opponent Not Found")
                    self.connection.send(segmentNotFound.get_segment_bytes(), client[1])
            else:
                print(f"[Client {client[1][0]}:{client[1][1]}] File Transfer")
                if(self.three_way_handshake(client[0], client[1])):
                    self.send_file(client[1])

    def send_file(self, client): 
        fileSize = os.path.getsize(f"in/{self.pathfile_input}")
        segment_count = math.ceil(fileSize/seg.PAYLOAD_SIZE)
        window = min(segment_count, WINDOW)
        sb = 0
        while sb < segment_count:
            sm = window
            for i in range(sm):
                print(
                    f"[!] [Client {client[0]}:{client[1]}] Sending Segment {sb + i}"
                )
                with open(f"in/{self.pathfile_input}", 'rb') as file:
                    file.seek((sb+i)*seg.PAYLOAD_SIZE)
                    data = file.read(seg.PAYLOAD_SIZE)
                    file.close()
                segment = seg.Segment()
                segment.set_seq_num(sb+i)
                segment.set_payload(data)
                segment.update_checksum()
                self.connection.send(segment.get_segment_bytes(), client)

            for i in range(sm):
                try:
                    data, _ = self.connection.listen(3)
                except:
                    break
                segment = seg.Segment()
                segment.set_segment_bytes(data)
                if(segment.get_flag().is_ack() and segment.get_ack_num() == sb+1):
                    print(
                        f"[!] [Client {client[0]}:{client[1]}] Received ACK {sb+1}"
                    )
                    sb += 1
                    window = min(segment_count - sb, WINDOW)
                elif(segment.get_flag().is_syn()):
                    break
        print(f"[!] [Client {client[0]}:{client[1]}] [CLS] File transfer completed, initiating closing connection...")
        print(f"[!] [Client {client[0]}:{client[1]}] [FIN] Sending FIN...")
        segment = seg.Segment()
        segment.set_flag(["FIN"])
        self.connection.send(segment.get_segment_bytes(), client)

    def tictactoe(self, addrs):
        print("\nStart")
        state = "000000000"
        turn = 0
        segmentState = seg.Segment()
        segmentState.set_flag(["ACK"])
        segmentState.set_payload((state+"1").encode())
        segmentState.update_checksum()
        self.connection.send(segmentState.get_segment_bytes(), addrs[0])
        segmentState.set_payload((state+"0").encode())
        segmentState.update_checksum()
        self.connection.send(segmentState.get_segment_bytes(), addrs[1])
        while True:
            data, addr = self.connection.listen()
            segmentResponse = seg.Segment()
            segmentResponse.set_segment_bytes(data)
            if(addrs[turn] == addr and segmentResponse.get_flag().is_ack()):
                if(segmentResponse.is_valid_checksum()):
                    if(turn == 0):
                        boxNumber = int(segmentResponse.get_payload().decode("utf-8")[0])
                        index = boxNumber-1
                        new_char = 'O'
                        string_list = list(state)
                        string_list[index] = new_char
                        state = "".join(string_list)
                        if self.checkConsecutive(state, "O"):
                            segmentState.set_flag(["FIN"])
                            segmentState.set_payload(b"You Won")
                            segmentState.update_checksum()
                            self.connection.send(segmentState.get_segment_bytes(), addrs[0])
                            segmentState.set_payload(b"You Lose")
                            segmentState.update_checksum()
                            self.connection.send(segmentState.get_segment_bytes(), addrs[1])
                            break
                        else:
                            segmentState.set_flag(["ACK"])
                            segmentState.set_payload((state+"0").encode())
                            segmentState.update_checksum()
                            self.connection.send(segmentState.get_segment_bytes(), addrs[0])
                            segmentState.set_payload((state+"1").encode())
                            segmentState.update_checksum()
                            self.connection.send(segmentState.get_segment_bytes(), addrs[1])
                    else:
                        boxNumber = int(segmentResponse.get_payload().decode("utf-8")[0])
                        index = boxNumber-1
                        new_char = 'X'
                        string_list = list(state)
                        string_list[index] = new_char
                        state = "".join(string_list)
                        if self.checkConsecutive(state, "X"):
                            segmentState.set_flag(["FIN"])
                            segmentState.set_payload(b"You Won")
                            segmentState.update_checksum()
                            self.connection.send(segmentState.get_segment_bytes(), addrs[1])
                            segmentState.set_payload(b"You Lose")
                            segmentState.update_checksum()
                            self.connection.send(segmentState.get_segment_bytes(), addrs[0])
                            break
                        else:
                            segmentState.set_flag(["ACK"])
                            segmentState.set_payload((state+"1").encode())
                            segmentState.update_checksum()
                            self.connection.send(segmentState.get_segment_bytes(), addrs[0])
                            segmentState.set_payload((state+"0").encode())
                            segmentState.update_checksum()
                            self.connection.send(segmentState.get_segment_bytes(), addrs[1])
                    turn = (turn+1) % 2
                    print("[!] State")
                    row = "   "
                    for i in range(9):
                        if(state[i] == "0"):
                            row += str(i+1)
                        elif(state[i] == "X"):
                            row += "X"
                        else:
                            row += "O"
                        if(i % 3 == 2):
                            print(row)
                            row = "   "  
                else:
                    segmentResponse.set_flag(["SYN"])
                    self.connection.send(segmentResponse.get_segment_bytes(), addr)
            elif(addrs[turn] == addr and segmentResponse.get_flag().is_syn()):
                segmentState.set_flag(["ACK"])
                segmentState.set_payload((state+"1").encode())
                segmentState.update_checksum()
                self.connection.send(segmentState.get_segment_bytes(), addr)
            elif(addrs[turn] != addr and segmentResponse.get_flag().is_syn()):
                segmentState.set_flag(["ACK"])
                segmentState.set_payload((state+"0").encode())
                segmentState.update_checksum()
                self.connection.send(segmentState.get_segment_bytes(), addr)

    def checkConsecutive(self, state, char):
        won = False
        for i in range(3):
            if(state[0+i] == state[3+i] and state[3+i] == state[6+i] and state[0+i] == char):
                won = True
            if(state[0+i*3] == state[1+i*3] and state[1+i*3] == state[2+i*3] and state[0+3*i] == char):
                won = True
        if(((state[0] == state[4] and state[4] == state[8]) or (state[2] == state[4] and state[4] == state[6])) and state[4] == char):
            won = True
        return won

s = Server()
s.listen_broadcast()
s.run()