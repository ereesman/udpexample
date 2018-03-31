import os
import sys
import socket
import hashlib
import time
from struct import *
'''
UDP client
'''

CLIENT_PORT = 5006


def run_client(ip, port, p1, p2, p3, out_file):

    try:
        os.remove(out_file)  # remove out_file if it already exists
    except:
        print "out_file doesn't exist yet"

    JOIN_REQ = pack('=h', 1)
    PASS_RESP_1 = pack('=h20s', 5, p1)
    PASS_RESP_2 = pack('=h20s', 5, p2)
    PASS_RESP_3 = pack('=h20s', 5, p3)

    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    send_sock.sendto(JOIN_REQ, (ip, int(port)))

    listen_sock.bind((ip, CLIENT_PORT))
    while True:
        time.sleep(0.5)  # because...packet loss!
        print "client listening..."
        packet = listen_sock.recv(1024)  # buffer size is 1024 bytes
        try:
            unpacked = unpack('=h', packet)
            if unpacked[0] == 2:  # PASS_REQ
                send_sock.sendto(PASS_RESP_1, (ip, int(port)))
                send_sock.sendto(PASS_RESP_2, (ip, int(port)))
                send_sock.sendto(PASS_RESP_3, (ip, int(port)))
            elif unpacked[0] == 4:  # REJECT
                print "failed to login..."
        except:
            print "packet header format is not '=h'"
        try:
            unpacked = unpack('=hi1000s', packet)
            print unpacked[1]
            if unpacked[0] == 7:  # DATA
                with open(out_file, 'ab') as out:
                    out.write(unpacked[2].strip('\x00'))
            out.close
        except:
            print "packet header format is not '=hi1000s'"
        try:
            unpacked = unpack('=h100s', packet)
            print unpacked
            if unpacked[0] == 6:  # TERMINATE
                try:
                    digest = hashlib.sha1()
                    with open(out_file, 'rb') as out:
                        block = out.read(1000)
                        while len(block) > 0:
                            digest.update(block)
                            block = out.read(1000)
                        out.close()
                except:
                    print "calculating digest failed"
                print digest.hexdigest()
                print unpacked[1].strip('\x00')
                if digest.hexdigest() == unpacked[1].strip('\x00'):
                    print "OK!"
                else:
                    print "digests do not match! ABORT!"
        except:
            print "packet header format is not '=h100s'"


if __name__ == '__main__':
    run_client(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5],
               sys.argv[6])
