import sys
import lib.connection as conn
import lib.segment as seg
from lib.parser import Parser
from socket import timeout as socket_timeout


class Client:
    def __init__(self):
        args = Parser(is_client=True)
        client_port, broadcast_port, pathfile_output = args.get_values()

        self.ip = conn.IP
        self.broadcast_port = broadcast_port
        self.client_port = client_port
        self.pathfile_output = pathfile_output
        self.segment = seg.Segment()
        if(pathfile_output == "tictactoe"):
            self.segment.set_payload(b"tictactoe")
        self.connection = conn.Connection(port=client_port, broadcast_port=broadcast_port, is_client=True)

    def three_way_handshake(self):
        print("[!] Initiating three way handshake...")

        try:
            # Sending SYN
            self.segment.set_flag(["SYN"])
            self.connection.send(self.segment.get_segment_bytes(), (self.connection.ip, self.broadcast_port))
            print(f"[!] [Handshake] Sending SYN request to server {self.connection.ip}:{self.broadcast_port}")
            print(f"   flag: SYN   Seq_num: {self.segment.get_seq_num()}   ack_num: {self.segment.get_ack_num()}")        

            # Reveiving SYN ACK
            print("[!] [Handshake] Waiting for response...")
            data, addr = self.connection.listen()

            self.segment.set_segment_bytes(data)
            flag = self.segment.get_flag()
            if (flag.is_syn() and flag.is_ack()):
                print(f"[!] [Handshake] Received SYN ACK request from server {addr[0]}:{addr[1]}")
                print(f"   flag: SYN ACK   Seq_num: {self.segment.get_seq_num()}   ack_num: {self.segment.get_ack_num()}")   
                # Sending ACK
                self.segment.set_flag(["ACK"])
                self.segment.set_ack_num(self.segment.get_seq_num() + 1)
                self.segment.set_seq_num(0)
                self.segment.update_checksum()
                self.connection.send(self.segment.get_segment_bytes(), addr)
                print(f"[!] [Handshake] Sending ACK request to server {addr[0]}:{addr[1]}")
                print(f"   flag: ACK   Seq_num: {self.segment.get_seq_num()}   ack_num: {self.segment.get_ack_num()}")
                return True
            return False
        except TimeoutError:
            print("[ERR] [Handshake] Timed out")
            return False
    
    def sendACK(self, addr, ackNumber):
        self.segment = seg.Segment()
        self.segment.set_flag(["ACK"])
        self.segment.set_seq_num(ackNumber-1)
        self.segment.set_ack_num(ackNumber)
        self.connection.send(self.segment.get_segment_bytes(), addr)
         
    def listen_file_transfer(self):
        print("[!] Initiating request to server...")
        rn = 0
        data = None
        addr = None
        while True:
            try:
                data, addr = self.connection.listen()
                if addr[1] == self.broadcast_port:
                    self.segment.set_segment_bytes(data)
                    if (self.segment.is_valid_checksum() and self.segment.get_flag() != seg.FIN and rn == self.segment.get_seq_num()):
                        payload = self.segment.get_payload()
                        file = open(f"out/{self.pathfile_output}", 'ab')
                        file.write(payload)
                        file.close()
                        print(f"[!] [Server {addr[0]}:{addr[1]}] Received Segment {rn}")
                        rn += 1
                        self.sendACK(addr, rn)
                        continue
                    elif self.segment.get_flag().is_fin():
                        print(f"[!] [Server {addr[0]}:{addr[1]}] Received FIN")
                        break
                    elif not (self.segment.is_valid_checksum()) or (rn < self.segment.get_seq_num()):
                        print("The port was corrupted")
                        # request resend
                        self.segment.set_flag(['SYN'])
                        self.connection.send(self.segment.get_segment_bytes(), addr)
                    else:
                        self.sendACK(addr, self.segment.get_seq_num()+1)
                else:
                    print(f"[!] [Server {addr[0]}:{addr[1]}] Received Segment {self.segment.get_seq_num()} [Wrong port]")
            except socket_timeout:
                print(f"[!] [Server {addr[0]}:{addr[1]}] [TIMEOUT] timeout error, resending previous sequence number")   
                self.sendACK(addr, rn)
              
        print(f"[!] [Server {addr[0]}:{addr[1]}] Data received successfully")
        print(f"[!] [Server {addr[0]}:{addr[1]}] Writing file to out/{self.pathfile_output}")
        sys.exit(0)
    
    def tictactoe(self):
        print("\nTic tac Toe")
        boxNumber = "0"
        while True:
            data, addr = self.connection.listen()
            segment = seg.Segment()
            segment.set_segment_bytes(data)
            if(segment.get_flag().is_fin()):
                print(f"[Server] {segment.get_payload().decode("utf-8")}")
                break
            elif(segment.get_flag().is_ack()):
                if(segment.is_valid_checksum()):
                    state = segment.get_payload().decode("utf-8")
                    row = ""
                    for i in range(9):
                        if(state[i] == "0"):
                            row += str(i+1)
                        elif(state[i] == "X"):
                            row += "X"
                        else:
                            row += "O"
                        if(i % 3 == 2):
                            print(row)
                            row = ""  
                    if(state[9] == "1"):
                        boxNumber = input("Select number: ")
                        segment.set_flag(["ACK"])
                        segment.set_payload(boxNumber.encode())
                        segment.update_checksum()
                        self.connection.send(segment.get_segment_bytes(), addr)
                    else:
                        print("Wait for opponent")
                else:
                    segment.set_flag(["SYN"])
                    self.connection.send(segment.set_segment_bytes(), addr)
            else:
                segment.set_flag(["ACK"])
                segment.set_payload(boxNumber.encode())
                segment.update_checksum()
                self.connection.send(segment.get_segment_bytes(), addr)

            
c = Client()
if(c.three_way_handshake()):
    if(c.pathfile_output == "tictactoe"):
        c.tictactoe()
    else:
        c.listen_file_transfer()