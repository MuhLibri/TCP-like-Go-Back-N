import struct


# CONSTANTS
# Flags
SYN = 0b00000010
ACK = 0b00010000
FIN = 0b00000001

# Checksum
BIT_SIZE = 16
MASKING_BIT = 0XFFFF

SEGMENT_SIZE = 32768
PAYLOAD_SIZE = SEGMENT_SIZE - 12


class SegmentFlag:
    def __init__(self, flag=0b0):
        self.syn = SYN & flag
        self.ack = ACK & flag
        self.fin = FIN & flag
        
    def is_syn(self):
        return self.syn != 0

    def is_ack(self):
        return self.ack != 0
    
    def is_fin(self):
        return self.fin != 0

    def get_flag(self):
        return self.syn | self.ack | self.fin

    def get_flag_bytes(self) -> bytes:
        return struct.pack("!B", self.syn | self.ack | self.fin)


class Segment:
    def __init__(self):
        self.seq_num = 0 
        self.ack_num = 0
        self.flag = SegmentFlag()
        self.checksum = 0
        self.payload = b""

    # Setter
    def set_seq_num(self, seq_num):
        self.seq_num = seq_num

    def set_ack_num(self, ack_num):
        self.ack_num = ack_num

    def set_flag(self, flags):
        flag = 0b0
        if "SYN" in flags:
            flag |= SYN
        if "ACK" in flags:
            flag |= ACK
        if "FIN" in flags:
            flag |= FIN

        self.flag = SegmentFlag(flag)

    def set_payload(self, payload):
        self.payload = payload

    # Getter
    def get_seq_num(self):
        return self.seq_num
    
    def get_ack_num(self):
        return self.ack_num
    
    def get_flag(self):
        return self.flag

    def get_payload(self):
        return self.payload

    # Set segment based on received bytes
    def set_segment_bytes(self, bytes_seg):
        self.seq_num = struct.unpack("!I", bytes_seg[0:4])[0]
        self.ack_num = struct.unpack("!I", bytes_seg[4:8])[0]
        self.flag = SegmentFlag(struct.unpack("!B", bytes_seg[8:9])[0])
        self.checksum = struct.unpack("!H", bytes_seg[10:12])[0]
        self.payload = bytes_seg[12:]

    # Transfrom segment into bytes
    def get_segment_bytes(self) -> bytes:
        seg_bytes = struct.pack("!II", self.seq_num, self.ack_num)
        seg_bytes += self.flag.get_flag_bytes()
        seg_bytes += struct.pack("!x")
        seg_bytes += struct.pack("!H", self.checksum)
        seg_bytes += self.payload
        return seg_bytes

    # Using 16-bit one complement checksum
    def __calculate_checksum(self) -> bytes:
        checksum = 0
        self.checksum = 0
        segment_byte = bin(int.from_bytes(self.get_segment_bytes()))[2:]

        for i in range(0, len(segment_byte), BIT_SIZE):
            chunk = segment_byte[i:i+BIT_SIZE]
            checksum += int(chunk, 2)
            checksum = (checksum & MASKING_BIT) + (checksum >> BIT_SIZE)

        checksum = ~checksum & MASKING_BIT
        return checksum

    # Update checksum based on __calculate_checksum method
    def update_checksum(self):
        self.checksum = self.__calculate_checksum()

    # Validating payload with checksum
    def is_valid_checksum(self) -> bool:
        bin_sum = self.checksum
        temp_sum = self.checksum
        self.checksum = 0
        segment_byte = bin(int.from_bytes(self.get_segment_bytes()))[2:]

        for i in range(0, len(segment_byte), BIT_SIZE):
            chunk = segment_byte[i:i+BIT_SIZE]
            bin_sum += int(chunk, 2)
            bin_sum = (bin_sum & MASKING_BIT) + (bin_sum >> BIT_SIZE)

        self.checksum = temp_sum
        return bin_sum == MASKING_BIT