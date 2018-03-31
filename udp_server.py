import sys
import socket
import hashlib
import time
from struct import *
'''
UDP server
'''

UDP_IP = "127.0.0.1"
CLIENT_PORT = 5006


def run_server(port, password, input_file):

    data_chunk = 1000  # 1000 byte chunks

    # calculate digest of input file

    digest = hashlib.sha1()
    with open(input_file, 'rb') as in_file:
        block = in_file.read(1000)
        while len(block) > 0:
            digest.update(block)
            block = in_file.read(1000)
    print "DIGEST:", digest.hexdigest()
    in_file.close()

    PASS_REQ = pack('=h', 2)
    PASS_ACCEPT = pack('=h', 3)
    REJECT = pack('=h', 4)
    TERMINATE = pack('=h100s', 6, digest.hexdigest())
    # DATA = pack('=hi1000s', 7, pkt_id, data)

    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listen_sock.bind((UDP_IP, int(port)))
    while True:
        print "server listening..."
        packet = listen_sock.recv(1024)  # buffer size is 1024 bytes
        try:
            unpacked = unpack('=h', packet)  # JOIN_REQ
            send_sock.sendto(PASS_REQ, (UDP_IP, CLIENT_PORT))
        except:
            print "packet header format is not '=h'"
        try:
            unpacked = unpack('=h20s', packet)  # PASS_RESP
            if unpacked[1].strip('\x00') == password:
                with open(input_file, 'rb') as in_file:
                    pkt_id = 1
                    while True:
                        time.sleep(0.5)  # because...packet loss!
                        data = in_file.read(data_chunk)
                        if len(data) == 0:
                            send_sock.sendto(TERMINATE, (UDP_IP, CLIENT_PORT))
                            in_file.close()
                            break
                        send_sock.sendto(
                            pack('=hi1000s', 7, pkt_id, data), (UDP_IP,
                                                                CLIENT_PORT))
                        pkt_id += 1
            else:
                send_sock.sendto(REJECT, (UDP_IP, CLIENT_PORT))
        except:
            print "packet header format is not '=h20s'"


if __name__ == '__main__':
    run_server(sys.argv[1], sys.argv[2], sys.argv[3])
